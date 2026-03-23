# Data Management — Transfermarkt Player Value Prediction

## 项目背景

我们正在做 NTU SC3021 Data Science Fundamentals 课程的 project，使用 Transfermarkt 的 football dataset 预测球员身价（market_value）。Data preparation（profiling、structuring、cleaning、enriching）已全部完成，现在需要完成 **Data Management** 部分。

这个 notebook 需要展示我们如何用关系型数据库管理项目数据，**严格对齐课程 slides 的四大学习目标**：
1. 概念设计（ER modeling）与逻辑设计（relational schema）
2. 用 SQL DDL 建表和管理数据状态
3. 用 SQL DML 查询数据，覆盖 data science 常用操作
4. 性能与可扩展性反思

---

## 文件路径

### 原始 8 个数据源
```
football-datasets/player_performances/player_performances.csv          # 1,878,719 rows — 比赛表现（spine table）
football-datasets/player_profiles/player_profiles.csv                  # 92,671 rows — 球员属性 + 出生日期
football-datasets/player_market_value/player_market_value.csv          # 901,429 rows — 历史身价（target variable 来源）
football-datasets/player_injuries/player_injuries.csv                  # 143,195 rows — 伤病记录
football-datasets/player_national_performances/player_national_performances.csv  # 92,701 rows — 国际比赛数据
football-datasets/team_competitions_seasons/team_competitions_seasons.csv        # 196,378 rows — 联赛映射
football-datasets/transfer_history/transfer_history.csv                # 1,101,440 rows — 转会记录
football-transfers-data/dataset/transfers.csv                          # 70,006 rows — 补充数据集 B
```

### Pipeline 输出
```
TransferValue/v2/outputs/enriched/enriched_player_dataset.csv          # 353,422 rows × 63 cols（含标识符，用于 EDA）
TransferValue/v2/outputs/enriched/enriched_modeling_ready.csv          # 353,422 rows × 50 cols（建模用）
TransferValue/v2/outputs/cleaned/cleaned_player_dataset.csv            # 353,422 rows × 39 cols
TransferValue/v2/outputs/structured/structured_player_dataset.csv      # 353,422 rows × 39 cols
```

**请先用 `ls` 确认实际路径，以上路径可能需要微调。优先使用 `enriched_player_dataset.csv`（63列完整版）作为数据源。**

---

## 技术要求

- **Python + sqlite3**（标准库，无需安装）
- 所有 SQL 操作必须用**原始 SQL 字符串**执行（不要用 pandas 的 `to_sql` 做建表，要手写 `CREATE TABLE` 和 `INSERT`）
- 查询结果可以用 `pd.read_sql_query()` 转成 DataFrame 展示
- ER 图用 **matplotlib + matplotlib.patches** 画（不要用 graphviz，避免安装依赖）
- 输出为 **一个完整的 `.ipynb` Jupyter Notebook**
- **语言**：代码注释用英文，Markdown 说明单元格用中文
- Markdown 和代码单元格交替出现，结构清晰

---

## 详细步骤

### Step 0: 环境准备与数据探查

```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load the enriched dataset
df = pd.read_csv("path/to/enriched_player_dataset.csv")
print(f"Shape: {df.shape}")
print(df.dtypes)
print(df.head())
```

先看一眼数据的列名和类型，再进行后续设计。

---

### Step 1: 概念设计 — ER 模型（Conceptual Design）

**目标**：根据我们的数据，识别实体和关系，画出 ER 图。

请从 enriched_player_dataset.csv 的 63 列中，识别出以下实体类型（按领域知识拆分，而不是把所有列塞进一张表）：

| Entity Type | 说明 | 核心属性 |
|------------|------|---------|
| **Player** | 球员基本信息 | player_id (PK), player_name, height, citizenship, is_eu, position, main_position, foot |
| **Season_Performance** | 球员每赛季的比赛表现 | player_id (FK→Player), season (组合PK), goals, assists, own_goals, minutes_played, yellow_cards, red_cards, clean_sheets, goals_conceded, appearances, penalty_goals, num_teams, primary_team_id, primary_team_name |
| **Market_Valuation** | 球员每赛季的身价 | player_id (FK→Player), season (组合PK), market_value, market_value_start, market_value_change, market_value_change_pct |
| **Injury_Record** | 球员每赛季的伤病汇总 | player_id (FK→Player), season (组合PK), injury_count, total_days_missed, total_games_missed, max_single_injury_days |
| **International_Career** | 球员国际比赛生涯汇总 | player_id (FK→Player, PK), intl_caps, intl_goals |
| **Transfer_Record** | 球员每赛季的转会记录 | player_id (FK→Player), season (组合PK), num_transfers, total_transfer_fee, max_transfer_fee, had_loan |
| **League** | 联赛信息 | competition_id (PK), competition_name, club_division, league_tier, is_top_division |

**关系**：
- Player → Season_Performance: 1:N（一个球员有多个赛季表现）
- Player → Market_Valuation: 1:N
- Player → Injury_Record: 1:N
- Player → International_Career: 1:1（汇总到球员级别）
- Player → Transfer_Record: 1:N
- Season_Performance → League: N:1（每条赛季表现对应一个联赛）

**ER 图要求**：
- 用 matplotlib 画，矩形表示实体，菱形表示关系，椭圆表示属性
- 标注主键（下划线）和基数（1:N, 1:1）
- 在 Markdown 单元格中用中文解释为什么这样拆分（减少冗余、保证数据一致性）

---

### Step 2: 逻辑设计 — 关系模式（Logical Design）

**目标**：将 ER 模型转为关系模式，遵循课程 slides 的三步转换算法。

在 Markdown 单元格中列出最终的关系模式（精简表示法）：

```
Player(player_id, player_name, height, citizenship, is_eu, position, main_position, foot)
    PK: player_id

Season_Performance(player_id → Player, season, goals, assists, own_goals, minutes_played,
    yellow_cards, red_cards, clean_sheets, goals_conceded, appearances, penalty_goals,
    num_teams, primary_team_id, primary_team_name, competition_id → League)
    PK: (player_id, season)

Market_Valuation(player_id → Player, season, market_value, market_value_start,
    market_value_change, market_value_change_pct)
    PK: (player_id, season)

Injury_Record(player_id → Player, season, injury_count, total_days_missed,
    total_games_missed, max_single_injury_days)
    PK: (player_id, season)

International_Career(player_id → Player, intl_caps, intl_goals)
    PK: player_id

Transfer_Record(player_id → Player, season, num_transfers, total_transfer_fee,
    max_transfer_fee, had_loan)
    PK: (player_id, season)

League(competition_id, competition_name, club_division, league_tier, is_top_division)
    PK: competition_id
```

然后解释精简合并的决策（比如 1:1 的 International_Career 理论上可以合并进 Player，但为了减少 NULL 和保持清晰，保持独立）。

---

### Step 3: SQL DDL — 建表与数据导入

**目标**：用 CREATE TABLE 建表，从 CSV 导入数据，演示 INSERT/UPDATE/DELETE。

#### 3.1 建表（含完整约束）

```python
conn = sqlite3.connect(':memory:')  # 或者保存到文件 'transfermarkt.db'
conn.execute("PRAGMA foreign_keys = ON")  # SQLite 默认不启用外键检查
cursor = conn.cursor()
```

为每张表写 **完整的 CREATE TABLE**，包含：
- `PRIMARY KEY`
- `FOREIGN KEY ... REFERENCES ...`
- `NOT NULL`（对关键字段）
- `CHECK` 约束（如 `market_value >= 0`, `goals >= 0`）

**注意建表顺序**：先建被引用的表（Player, League），再建引用它们的表。

#### 3.2 数据导入

从 enriched_player_dataset.csv 读取数据后，拆分到各表中，用 **`INSERT INTO ... VALUES ...`** 逐表插入。

```python
# Load full dataset
df = pd.read_csv("path/to/enriched_player_dataset.csv")

# Extract Player table (deduplicated at player level)
player_df = df.drop_duplicates(subset='player_id')[['player_id', 'player_name', 'height', ...]]

# Insert into Player table
for _, row in player_df.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO Player (player_id, player_name, height, ...)
        VALUES (?, ?, ?, ...)
    """, (row['player_id'], row['player_name'], row['height'], ...))

conn.commit()
```

对每张表都做类似操作。插入后用 `SELECT COUNT(*) FROM 表名` 验证行数。

#### 3.3 演示 UPDATE 和 DELETE

```sql
-- UPDATE 示例：修正某球员的身高数据
UPDATE Player SET height = 170.0 WHERE player_id = 28003 AND height IS NULL;

-- DELETE 示例：删除没有任何出场记录的伤病记录（数据清理场景）
DELETE FROM Injury_Record WHERE player_id NOT IN (SELECT player_id FROM Season_Performance);
```

每个操作前后都 SELECT 展示变化，并用中文 Markdown 解释操作的业务含义。

---

### Step 4: SQL DML — 查询操作（覆盖课程所有查询类型）

**目标**：用 SQL 查询演示 data science 中的常用操作。每个查询必须：
1. 有一个中文标题说明业务问题
2. 写出完整 SQL
3. 展示查询结果（用 pd.read_sql_query 转 DataFrame）
4. 简要中文说明结果含义

请依次实现以下 **9 类查询**：

---

#### 4.1 基础过滤（WHERE）

**业务问题**：找出身价超过 5000 万欧元的顶级球员

```sql
SELECT p.player_name, p.main_position, mv.season, mv.market_value
FROM Player p, Market_Valuation mv
WHERE p.player_id = mv.player_id
  AND mv.market_value > 50000000
ORDER BY mv.market_value DESC
LIMIT 20;
```

---

#### 4.2 多表 JOIN（至少涉及 3 张表）

**业务问题**：查询每个球员的姓名、赛季进球数和对应赛季身价

```sql
SELECT p.player_name, sp.season, sp.goals, mv.market_value
FROM Player p, Season_Performance sp, Market_Valuation mv
WHERE p.player_id = sp.player_id
  AND p.player_id = mv.player_id
  AND sp.season = mv.season
  AND sp.goals > 20
ORDER BY mv.market_value DESC
LIMIT 20;
```

**重要**：确保所有 tuple variable 都通过 join condition 连接（slides 强调的准则）。

---

#### 4.3 LEFT OUTER JOIN

**业务问题**：查询所有球员，包括没有伤病记录的球员

```sql
SELECT p.player_name, p.main_position, ir.injury_count, ir.total_days_missed
FROM Player p
LEFT OUTER JOIN Injury_Record ir
  ON p.player_id = ir.player_id
WHERE ir.injury_count IS NULL
LIMIT 20;
```

说明：LEFT OUTER JOIN 保留左表所有行，即使右表没有匹配。

---

#### 4.4 聚合函数（COUNT, AVG, MAX, MIN, SUM）

**业务问题**：数据集的整体统计概览

```sql
-- 简单聚合：数据集中有多少球员？平均身价是多少？最高身价是多少？
SELECT COUNT(DISTINCT player_id) AS total_players,
       AVG(market_value) AS avg_market_value,
       MAX(market_value) AS max_market_value,
       MIN(market_value) AS min_market_value
FROM Market_Valuation;
```

---

#### 4.5 GROUP BY

**业务问题**：各位置的平均身价和平均进球数

```sql
SELECT p.main_position,
       COUNT(*) AS player_seasons,
       AVG(mv.market_value) AS avg_value,
       AVG(sp.goals) AS avg_goals
FROM Player p, Season_Performance sp, Market_Valuation mv
WHERE p.player_id = sp.player_id
  AND p.player_id = mv.player_id
  AND sp.season = mv.season
GROUP BY p.main_position;
```

---

#### 4.6 HAVING

**业务问题**：找出平均身价超过 1000 万的联赛

```sql
SELECT l.competition_name, l.league_tier,
       COUNT(*) AS num_records,
       AVG(mv.market_value) AS avg_value
FROM League l, Season_Performance sp, Market_Valuation mv
WHERE l.competition_id = sp.competition_id
  AND sp.player_id = mv.player_id
  AND sp.season = mv.season
GROUP BY l.competition_id, l.competition_name
HAVING AVG(mv.market_value) > 10000000
ORDER BY avg_value DESC;
```

---

#### 4.7 DISTINCT

**业务问题**：数据集中覆盖了多少个不同国籍的球员？

```sql
SELECT COUNT(DISTINCT citizenship) AS num_nationalities
FROM Player
WHERE citizenship IS NOT NULL;
```

---

#### 4.8 UNION

**业务问题**：合并"身价飙升球员"和"身价暴跌球员"两个子集

```sql
-- 身价上涨超过 100% 的球员
SELECT p.player_name, mv.season, mv.market_value_change_pct, 'Rising Star' AS category
FROM Player p, Market_Valuation mv
WHERE p.player_id = mv.player_id
  AND mv.market_value_change_pct > 1.0

UNION

-- 身价下跌超过 50% 的球员
SELECT p.player_name, mv.season, mv.market_value_change_pct, 'Declining' AS category
FROM Player p, Market_Valuation mv
WHERE p.player_id = mv.player_id
  AND mv.market_value_change_pct < -0.5

ORDER BY market_value_change_pct DESC
LIMIT 20;
```

---

#### 4.9 复杂嵌套查询（子查询 / 多条件 JOIN）

**业务问题**：找出在五大联赛效力、有国际比赛经历、且赛季进球超过 15 的球员及其身价（涉及 5 张表）

```sql
SELECT p.player_name, sp.season, sp.goals, ic.intl_caps,
       l.competition_name, mv.market_value
FROM Player p
JOIN Season_Performance sp ON p.player_id = sp.player_id
JOIN Market_Valuation mv ON p.player_id = mv.player_id AND sp.season = mv.season
JOIN International_Career ic ON p.player_id = ic.player_id
JOIN League l ON sp.competition_id = l.competition_id
WHERE l.is_top_division = 1
  AND l.competition_id IN ('GB1', 'ES1', 'IT1', 'L1', 'FR1')
  AND ic.intl_caps > 0
  AND sp.goals > 15
ORDER BY mv.market_value DESC
LIMIT 20;
```

---

### Step 5: 性能与可扩展性反思

在 Notebook 末尾写一段 Markdown 讨论（中文），覆盖以下三点：

**5.1 关系型数据库 vs 直接操作 CSV/DataFrame**
- 数据一致性：外键约束保证引用完整性（如 Season_Performance 中的 player_id 一定存在于 Player 表）
- 约束检查：NOT NULL、CHECK 自动拒绝不合法数据
- 避免冗余：球员基本信息只存一份，不像 flat CSV 中每行都重复
- 并发访问与事务支持

**5.2 索引对查询性能的影响**
- 主键上自动创建索引，所以 `WHERE player_id = xxx` 很快
- 外键列（如 Season_Performance.player_id）如果创建索引，JOIN 操作会显著加速
- 可以演示 `CREATE INDEX` 并用 `EXPLAIN QUERY PLAN` 对比

**5.3 可扩展性**
- 当前 353K 行在 SQLite 内存模式下秒级完成，但如果数据增长到百万级，可能需要：
  - 迁移到 PostgreSQL/MySQL
  - 对频繁查询的列建索引
  - 考虑分区表（按 season 分区）
  - 物化视图缓存常用聚合结果

---

## Notebook 结构总结

| Section | 内容 | 预计代码单元格 |
|---------|------|--------------|
| 0. Setup | 导包、加载数据、探查列名 | 2-3 |
| 1. ER Model | Markdown 解释 + matplotlib 画 ER 图 | 2-3 |
| 2. Relational Schema | Markdown 列出所有表的 schema + 解释 | 1-2 |
| 3. SQL DDL | CREATE TABLE × 7 + INSERT 数据 + UPDATE/DELETE 演示 | 8-12 |
| 4. SQL DML | 9 类查询，每类 1-2 个查询 | 12-18 |
| 5. Reflection | Markdown 讨论 + 可选的 INDEX 演示 | 2-3 |

**总计约 30-40 个单元格。**

---

## 注意事项

1. **SQLite 外键**：必须执行 `PRAGMA foreign_keys = ON` 才生效
2. **数据类型映射**：SQLite 没有严格类型系统，但 CREATE TABLE 中仍然要声明类型（INTEGER, REAL, TEXT, BOOLEAN）以体现 schema 设计
3. **INSERT 性能**：如果 iterrows 太慢，可以用 `executemany()` 批量插入，但代码中要体现出 INSERT 语句本身
4. **Boolean 处理**：SQLite 没有 BOOLEAN 类型，用 INTEGER (0/1) 代替，在 CREATE TABLE 中可以加 `CHECK(is_eu IN (0, 1))`
5. **NULL 处理**：enriched CSV 中的 NaN 要在插入时转为 Python 的 `None`，SQLite 会存为 NULL
6. **League 表去重**：从 enriched 数据中提取 League 信息时，需要 `drop_duplicates(subset='competition_id')`，因为同一个联赛出现在多行中
7. **ER 图**：不要用 graphviz（可能未安装），用 matplotlib 的 patches、FancyBboxPatch、FancyArrowPatch 手动画
8. **查询结果展示**：每个查询结果用 `pd.read_sql_query(sql, conn)` 读取并显示，限制 `LIMIT 20` 避免输出过长
