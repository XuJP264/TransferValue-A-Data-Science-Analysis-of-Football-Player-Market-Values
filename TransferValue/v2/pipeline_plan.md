# Data Preparation Pipeline v2 — 重建计划

## Context

当前 `TransferValue/` 中的数据准备流水线存在 13 个已确认问题（6 个高危），且**生成这些数据的代码不存在于仓库中**（仅有输出 CSV 和报告）。因此建议**完全重写**，而非修补。

新流水线输出至 `TransferValue/v2/`，保留原有 `TransferValue/` 内容不动。

### 关键约束
- 用户已从 Kaggle 重新下载 Dataset A，目录结构变为 `football-datasets/*/`（不再有 `datalake/transfermarkt/` 中间层）
- `player_performances.csv`（1,878,719 行）和 `transfer_history.csv`（1,101,440 行）现在是**真实数据**（LFS 问题已解决）
- `team_competitions_seasons.csv` 结构大变：从 28 列（含 wins/losses/rank/points）变为 **仅 7 列**（`club_id, team_name, season_id, competition_name, competition_id, club_division, _last_modified_at`）——**球队赛季战绩数据不可用**
- Dataset C 排除，仅使用 Dataset A + B

---

## 文件结构

```
TransferValue/v2/
├── pipeline_config.py          # 共享配置、路径、工具函数
├── stage1_profiling.py         # 数据探查 & 验证
├── stage2_structuring.py       # 多表 join → 球员-赛季粒度
├── stage3_cleaning.py          # 缺失值、异常值、类型修复
├── stage4_enriching.py         # 派生特征、编码
├── run_pipeline.py             # 主入口，顺序执行四个阶段
└── outputs/
    ├── profiling/
    ├── structured/
    ├── cleaned/
    └── enriched/
```

---

## Stage 1: Profiling (`stage1_profiling.py`)

**目标**：验证数据可用性，生成概况报告，不做任何变换。

- 验证所有 CSV 文件可读（非 LFS 指针）
- 对每个 CSV：行数、列数、dtype、缺失率、唯一值数、数值列 min/max/mean
- 验证 `player_id` 在所有表中的类型一致性
- 输出：`outputs/profiling/profiling_report.md` + `profiling_summary.json`

---

## Stage 2: Structuring (`stage2_structuring.py`)

**目标**：多表 join，生成统一的球员-赛季数据集。

### 2.1 加载并聚合 player_performances → 球员-赛季

- 解析 `minutes_played`（去掉 `'` 和 `.` 千位分隔符，如 `"1.580'"` → `1580.0`）
- 按 `(player_id, season_name)` 聚合：SUM goals/assists/own_goals/minutes_played/yellow_cards/red_cards/clean_sheets/goals_conceded/appearances
- 同一赛季多队时，取 `minutes_played` 最多的队作为 `primary_team`
- 数据现已完整可用（1,878,719 行），无需降级方案

### 2.2 加载 player_profiles（92,671 行）

- 保留：`player_id, player_name, date_of_birth, height, citizenship, is_eu, position, main_position, foot`
- `height == 0.0` → NaN

### 2.3 加载 player_market_value（901,429 行）— 修复问题 #2

- `date_unix` 字段实际为 ISO 日期（如 `"2023-12-19"`），非 unix 时间戳
- 每条记录转换为 `season_name`：月份 ≥ 8 → 当年开始的赛季，月份 ≤ 7 → 上一年开始的赛季
- 按 `(player_id, season_name)` 取**最接近赛季结束（6月30日）**的观测值作为 `market_value`
- 同时取最接近赛季开始（8月1日）的观测值作为 `market_value_start`

### 2.4 加载 player_injuries（143,195 行）

- 按 `(player_id, season_name)` 聚合：`injury_count`, `total_days_missed`, `total_games_missed`, `max_single_injury_days`

### 2.5 加载 player_national_performances（92,701 行）

- 按 `player_id` 聚合（一个球员可能代表多支国家队）：`intl_caps = SUM(matches)`, `intl_goals = SUM(goals)`

### 2.6 加载 team_competitions_seasons（196,378 行）

- **注意**：新版仅有 7 列（`club_id, team_name, season_id, competition_name, competition_id, club_division, _last_modified_at`），**无战绩数据**（无 wins/losses/rank/points）
- 用途降级为：提供 `competition_id`（联赛代码）和 `club_division`（联赛层级名称）
- Join key: `(primary_team_id = club_id, season_name ≈ season_id)`

### 2.7 加载 transfer_history（1,101,440 行）

- 按 `(player_id, season_name)` 聚合：`num_transfers, total_transfer_fee, max_transfer_fee, had_loan`

### 2.8 加载 Dataset B transfers.csv（70,006 行）

- 赛季转换：整数 `2009` → `"08/09"`
- 作为补充来源：提供 `player_age`（用于回填 age 缺失）和 `ds_b_league`（联赛代码如 GB1）

### 2.9 Master Join

- **脊柱表**：player_performances 聚合结果 `(player_id, season_name)`
- 依次 LEFT JOIN：profiles → market_value → injuries → national → team_context → transfer_history → dataset_b
- **计算 age（修复问题 #1）**：`age = (赛季中点日期 - date_of_birth) / 365.25`，缺失时用 Dataset B 的 `player_age` 回填

### 2.10 过滤（修复问题 #12）

- **删除 `market_value` 为空的行**——没有目标变量的行无法用于建模

### 输出 schema（约 40+ 列）

```
# 标识符
player_id (int64), player_name, season

# 球员属性
age, height, citizenship, is_eu, position, main_position, foot

# 比赛表现
goals, assists, own_goals, minutes_played, yellow_cards, red_cards,
clean_sheets, goals_conceded, appearances, penalty_goals, num_teams

# 目标变量
market_value, market_value_start

# 伤病
injury_count, total_days_missed, total_games_missed

# 国际赛
intl_caps, intl_goals

# 球队上下文（新版 team_competitions_seasons 无战绩，仅提供联赛信息）
primary_team_id, primary_team_name, primary_competition_id,
primary_competition_name, club_division

# 转会
num_transfers, total_transfer_fee, max_transfer_fee, had_loan, ds_b_league
```

---

## Stage 3: Cleaning (`stage3_cleaning.py`)

**目标**：类型修复、缺失值处理、异常值处理。注意：先清洗，再做特征工程（修复问题 #3）。

### 3.1 类型修复（修复问题 #13）
- `player_id` → `Int64`（pandas nullable integer）

### 3.2 去重
- 精确重复行删除
- `(player_id, season)` 重复时保留非空值更多的行

### 3.3 缺失值处理

| 列 | 策略 | 理由 |
|---|---|---|
| market_value | 应已无缺失（Stage 2 已过滤），若有残余则删除 | 目标变量不可填补 |
| age | 按 `(position, season)` 分组中位数填补残余缺失 | 修复问题 #1 后缺失率应 <3% |
| goals, assists | 按 `(position, competition, season)` 分组中位数填补 | 修复问题 #11 |
| minutes_played | 按 `(position, competition, season)` 分组中位数填补 | 分组感知 |
| height | 按 `position` 分组中位数填补 | |
| injury 列 | NaN → 0（无记录 = 无伤病） | |
| intl 列 | NaN → 0，has_intl → False | |
| transfer 列 | NaN → 0，had_loan → False | |
| club_division | 保持 NaN | 真实缺失，不宜硬填 |

### 3.4 异常值处理

| 列 | 策略 | 理由 |
|---|---|---|
| **market_value** | **不做任何裁剪**（修复问题 #5） | 目标变量必须保持真实分布 |
| goals | 领域知识上界 60，下界 0 | 梅西最高赛季 73 球（含所有赛事），60 以上为数据错误 |
| assists | 领域知识上界 40，下界 0 | |
| minutes_played | 上界 5500，下界 0 | 一赛季最多约 60 场 × 90 分 |
| yellow_cards, red_cards | 1st-99th 百分位裁剪 | |
| total_days_missed, total_games_missed | 1st-99th 百分位裁剪 | |

### 3.5 分类变量标准化
- `position` / `main_position`：统一为 Goalkeeper / Defender / Midfield / Attack 四大类
- `player_name`：strip whitespace，不做大小写转换

---

## Stage 4: Enriching (`stage4_enriching.py`)

**目标**：基于**已清洗**的数据创建派生特征（修复问题 #3）。

### 4.1 表现效率特征
```python
goals_per_90 = (goals / minutes_played) * 90      # minutes > 0
assists_per_90 = (assists / minutes_played) * 90
goal_contributions_per_90 = ((goals + assists) / minutes_played) * 90
yellow_cards_per_90 = (yellow_cards / minutes_played) * 90
clean_sheets_per_90 = (clean_sheets / minutes_played) * 90
goals_conceded_per_90 = (goals_conceded / minutes_played) * 90
```
分母为 0 时设为 0.0（非 NaN/inf）。

### 4.2 年龄特征（修复问题 #10 — 现在 age 已充分填充）
```python
age_squared = age ** 2
career_stage = cut(age, [0,21,24,28,32,50],
                   labels=['youth','emerging','prime','experienced','veteran'])
```

### 4.3 市场价值相关（修复问题 #6）
```python
market_value_change = market_value - market_value_start    # 赛季内身价变化
market_value_change_pct = market_value_change / market_value_start
```
**不创建 `log_market_value` 特征**。对数变换在建模阶段按需进行。

### 4.4 伤病特征
```python
injury_severity = total_days_missed / injury_count   # 0 if no injuries
was_injured = (injury_count > 0).astype(int)
```

### 4.5 国际赛经验
```python
intl_goals_per_cap = intl_goals / intl_caps   # caps > 0
has_intl_career = (intl_caps > 0).astype(int)
```

### 4.6 联赛编码（修复问题 #9）

新版 `team_competitions_seasons` 无战绩数据，球队上下文特征调整为：
```python
# 从 competition_id 和 club_division 提取联赛层级
# competition_id 示例: GB1, ES1, IT1, L1, FR1, BRA1, ...
# 用 competition_id 末尾数字推断层级（GB1=顶级, GB2=次级）
league_tier = extract_tier_from_competition_id(competition_id)  # 数值 1-5+
is_top_division = (league_tier == 1).astype(int)
```
- Big 5 联赛二值标记：`is_GB1, is_ES1, is_IT1, is_L1, is_FR1`（从 `primary_competition_id` 提取）
- **不使用 ordinal encoding 对 1400+ 联赛编码**

### 4.8 位置编码
- `main_position` One-Hot：`pos_Defender, pos_Midfield, pos_Attack`（Goalkeeper 作为基准）

### 4.9 排除无效特征
- **不创建** `fee_to_value_ratio`（修复问题 #8，97.67% 缺失）
- **不创建** `log_market_value` 特征（修复问题 #6，数据泄漏）

### 4.10 Post-Enrichment Validation（一致性校验）

在所有特征工程完成后，执行以下校验：
```python
# 1. 验证派生特征与原始值的数学一致性
assert (goals_per_90 == (goals / minutes_played) * 90).all()  # where minutes > 0
assert (age_squared == age ** 2).all()

# 2. 验证无 inf / NaN 泄漏（分母为 0 时应为 0.0）
assert not df[rate_columns].isin([np.inf, -np.inf]).any().any()

# 3. 验证目标变量 market_value 未被任何操作修改
assert df['market_value'].equals(cleaned_market_value)  # 与 cleaning 阶段输出对比

# 4. 验证 log_market_value 和 fee_to_value_ratio 不存在
assert 'log_market_value' not in df.columns
assert 'fee_to_value_ratio' not in df.columns
```
校验失败时抛出异常并记录到报告，不静默跳过。

### 输出
- `enriched_player_dataset.csv` — 全量含标识符列，供 EDA 使用
- `enriched_modeling_ready.csv` — 仅数值/编码列 + 目标变量，供建模使用

---

## 13 个问题修复对照表

| # | 问题 | 严重度 | 修复位置 |
|---|------|--------|----------|
| 1 | age 未从 DOB 计算 | HIGH | Stage 2.9 |
| 2 | market_value 仅用 latest 表 | HIGH | Stage 2.3 |
| 3 | 先特征工程后清洗 | HIGH | run_pipeline 顺序 |
| 4 | goals/assists IQR 过激 | HIGH | Stage 3.4 |
| 5 | market_value 被裁剪 | HIGH | Stage 3.4 |
| 6 | log_market_value 泄漏 | HIGH | Stage 4.9 |
| 7 | 丢弃有用特征 | MEDIUM | Stage 2 全程 |
| 8 | fee_to_value_ratio 无用 | MEDIUM | Stage 4.9 |
| 9 | league ordinal encoding | MEDIUM | Stage 4.7 |
| 10 | age 派生特征无效 | MEDIUM | Stage 4.2 |
| 11 | 非分组感知填补 | MEDIUM | Stage 3.3 |
| 12 | 空壳行未过滤 | MEDIUM | Stage 2.10 |
| 13 | player_id 为 float | LOW | Stage 3.1 |

---

## 验证方案

1. **运行 pipeline**：`python TransferValue/v2/run_pipeline.py`
2. **检查 profiling 报告**：确认 LFS 文件状态、各表行数列数与预期一致
3. **检查 structured 输出**：
   - `market_value` 缺失率应接近 0%（已过滤）
   - `age` 缺失率应 <5%（从 DOB 计算 + Dataset B 回填）
   - 行数应在 30-50 万范围（有身价记录的球员-赛季数）
4. **检查 cleaned 输出**：
   - `goals` 最大值 ≤ 60，`assists` 最大值 ≤ 40
   - `market_value` 无裁剪（最大值应在 1-2 亿欧元范围）
   - 无 NaN 在不应有缺失的列中
5. **检查 enriched 输出**：
   - `goals_per_90` 与 `goals / minutes_played * 90` 一致
   - 不存在 `log_market_value` 列
   - 不存在 `fee_to_value_ratio` 列
   - `league_encoded` 列不存在，取而代之是 `league_tier` + `is_GB1` 等
6. **读取每阶段的 report.md** 确认操作日志合理

---

## 关键依赖文件

所有文件现已可用（LFS 问题已解决），路径为新的扁平结构：

| 文件 | 行数 | 作用 |
|------|------|------|
| `football-datasets/player_market_value/player_market_value.csv` | 901,429 | 历史身价（目标变量来源） |
| `football-datasets/player_profiles/player_profiles.csv` | 92,671 | 球员属性 + DOB |
| `football-datasets/player_performances/player_performances.csv` | 1,878,719 | 比赛表现（脊柱表） |
| `football-datasets/transfer_history/transfer_history.csv` | 1,101,440 | 转会记录 |
| `football-datasets/player_injuries/player_injuries.csv` | 143,195 | 伤病数据 |
| `football-datasets/team_competitions_seasons/team_competitions_seasons.csv` | 196,378 | 联赛映射（仅 7 列，无战绩） |
| `football-datasets/player_national_performances/player_national_performances.csv` | 92,701 | 国家队数据 |
| `football-datasets/team_details/team_details.csv` | 2,175 | 球队元数据 |
| `football-transfers-data/dataset/transfers.csv` | 70,006 | Dataset B 转会数据 |
