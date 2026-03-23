# V2 Pipeline — Complete Operations Log

> Final output: **353,422 rows × 63 columns** (full) / **50 columns** (modeling-ready)
> Run command: `source venv/bin/activate && cd TransferValue/v2 && python3 run_pipeline.py`
> Run from a specific stage: `python3 run_pipeline.py --stage 3`

---

## File Structure

```
TransferValue/v2/
├── pipeline_config.py          # Shared config, paths, utility functions
├── stage1_profiling.py         # Stage 1: Data profiling
├── stage2_structuring.py       # Stage 2: Multi-table join
├── stage3_cleaning.py          # Stage 3: Cleaning
├── stage4_enriching.py         # Stage 4: Feature engineering
├── run_pipeline.py             # Main entry point (supports --stage N argument)
├── pipeline_plan.md            # Original plan document
├── pipeline_summary.md         # This file
└── outputs/
    ├── profiling/              # profiling_report.md, profiling_summary.json
    ├── structured/             # structured_player_dataset.csv (353K rows), structuring_report.md
    ├── cleaned/                # cleaned_player_dataset.csv (353K rows), cleaning_report.md
    └── enriched/               # enriched_player_dataset.csv (353K rows, 63 cols)
                                # enriched_modeling_ready.csv (353K rows, 50 cols)
                                # enriching_report.md
```

---

## Data Sources (8 CSVs)

| File | Rows | Purpose |
|------|------|---------|
| `football-datasets/player_performances/player_performances.csv` | 1,878,719 | Spine table (match performance) |
| `football-datasets/player_profiles/player_profiles.csv` | 92,671 | Player attributes + DOB |
| `football-datasets/player_market_value/player_market_value.csv` | 901,429 | Historical market value (target variable source) |
| `football-datasets/player_injuries/player_injuries.csv` | 143,195 | Injury records |
| `football-datasets/player_national_performances/player_national_performances.csv` | 92,701 | International team data |
| `football-datasets/team_competitions_seasons/team_competitions_seasons.csv` | 196,378 | League mapping (only 7 columns, no match results) |
| `football-datasets/transfer_history/transfer_history.csv` | 1,101,440 | Transfer records |
| `football-transfers-data/dataset/transfers.csv` | 70,006 | Dataset B (supplementary age and league info) |

---

## Stage 1: Profiling

**Objective**: Validate data availability. No transformations applied.

### Operations Performed
- Verified all 8 CSVs are readable (not Git LFS pointers)
- Generated per-CSV profiles: row count, column count, dtypes, missing rates, unique value counts, numeric column min/max/mean
- Checked `player_id` type consistency across all tables

### Outputs
- `outputs/profiling/profiling_report.md` — Human-readable report
- `outputs/profiling/profiling_summary.json` — Machine-readable JSON

---

## Stage 2: Structuring (Multi-Table Join)

**Objective**: Join 8 source tables into a unified player-season granularity dataset.

### Row Count Progression
```
1,878,719 (raw player_performances)
    ↓ Aggregated by (player_id, season_name)
  819,784 (unique player-seasons)
    ↓ Filtered rows where market_value is NaN (-443,683)
    ↓ Filtered rows where market_value == 0 (-22,679)
  353,422 (final)
```

### Per-Table Loading & Processing Methods

#### 2.1 player_performances → Player-Season Aggregation
- **minutes_played parsing**: Removed `'` and `.` (thousands separator), e.g. `"1.580'"` → `1580.0`
- **Aggregation**: Grouped by `(player_id, season_name)`, applied SUM on goals/assists/own_goals/minutes_played/yellow_cards/red_cards/clean_sheets/goals_conceded/appearances/penalty_goals
- **primary_team assignment**: When a player played for multiple teams in a season, selected the team with the highest minutes_played
- **num_teams**: Counted distinct teams per player-season
- **red_cards merge**: `second_yellow_cards + direct_red_cards → red_cards`

#### 2.2 player_profiles
- Retained fields: player_id, player_name, date_of_birth, height, citizenship, is_eu, position, main_position, foot
- `height == 0.0` → NaN
- `date_of_birth` converted to datetime

#### 2.3 player_market_value (fix issue #2)
- `date_unix` field is actually an ISO date (e.g. `"2023-12-19"`), not a unix timestamp
- Date → season mapping rule: month >= 8 → current year's season; month <= 7 → previous year's season
- `market_value`: Selected the observation closest to season end date (Jun 30)
- `market_value_start`: Selected the observation closest to season start date (Aug 1)

#### 2.4 player_injuries
- Aggregated by `(player_id, season_name)`: injury_count, total_days_missed, total_games_missed, max_single_injury_days

#### 2.5 player_national_performances
- Aggregated by `player_id` (player-level, not season-level): intl_caps = SUM(matches), intl_goals = SUM(goals)

#### 2.6 team_competitions_seasons
- season_id (integer, e.g. 2023) → season string `"22/23"`
- Provides only competition_id (league code) and club_division (league name)
- Deduplicated by (club_id, season_name), keeping the first record

#### 2.7 transfer_history
- Aggregated by `(player_id, season_name)`: num_transfers, total_transfer_fee, max_transfer_fee, had_loan
- Loan detection: transfer_type contains "loan"

#### 2.8 Dataset B transfers
- Season conversion: integer `2009` → `"08/09"`
- Provides player_age (to backfill missing age) and ds_b_league (league code)

### Master Join Order
1. Spine table: player_performances aggregation result
2. LEFT JOIN profiles (player-level)
3. LEFT JOIN market_value (player-season level)
4. LEFT JOIN injuries (player-season level)
5. LEFT JOIN national (player-level)
6. LEFT JOIN team_competitions (on primary_team_id + season_name)
7. LEFT JOIN transfer_history (player-season level)
8. LEFT JOIN Dataset B (player-season level)

### Age Calculation (fix issue #1)
- `age = (season midpoint Jan 15 - date_of_birth) / 365.25`
- Backfilled with Dataset B's player_age where computed age is missing

### Filtering (fix issue #12)
- Removed rows where `market_value` is NaN **or** equals 0

### Output
- `outputs/structured/structured_player_dataset.csv` — 353,422 rows × 39 columns

---

## Stage 3: Cleaning

**Objective**: Type fixes, deduplication, missing value handling, consistency fixes, outlier handling, categorical variable standardization. Cleaning is performed BEFORE feature engineering (fix issue #3).

### 3.1 Type Fixes (fix issue #13)
- `player_id` → `Int64` (pandas nullable integer)

### 3.2 Deduplication
- Removed exact duplicate rows
- For `(player_id, season)` duplicates, kept the row with fewer NaN values

### 3.3 Missing Value Handling

| Column | Strategy |
|--------|----------|
| market_value | Should already have no missing values; drop any residuals |
| age | Group median by (main_position, season) → global median fallback |
| goals, assists, minutes_played | Group median by (main_position, competition_id, season) → global median fallback |
| height | Group median by main_position → global median fallback |
| injury columns | NaN → 0 (no record = no injury) |
| international columns | NaN → 0 |
| transfer columns | NaN → 0, had_loan → False |
| club_division | Keep NaN (genuinely missing, should not be imputed) |

### 3.3b Data Consistency Fixes
- When `minutes_played == 0`, set goals/assists/own_goals/penalty_goals/yellow_cards/red_cards/clean_sheets/goals_conceded to zero
- Actual impact: goals 3 rows, assists 37,247 rows, yellow_cards 79,667 rows, etc.

### 3.4 Outlier Handling

| Column | Method | Range |
|--------|--------|-------|
| **market_value** | **No clipping** (fix issue #5) | Preserved as-is |
| goals | Domain-knowledge cap | [0, 60] |
| assists | Domain-knowledge cap | [0, 40] |
| minutes_played | Domain-knowledge cap | [0, 5500] |
| yellow_cards | 1st–99th percentile clipping | [0, 12] |
| red_cards | 1st–99th percentile clipping | [0, 2] |
| total_days_missed | 1st–99th percentile clipping | [0, 249] |
| total_games_missed | 1st–99th percentile clipping | [0, 33] |

### 3.5 Categorical Variable Standardization
- `main_position`: Unified into 4 categories (Goalkeeper / Defender / Midfield / Attack)
- `position`: Preserved original granularity (17 types, e.g. "Defender - Centre-Back", "Attack - Right Winger")
- `player_name`: Stripped whitespace + removed trailing `(player_id)` suffix (e.g. `"Messi (28003)"` → `"Messi"`)

### Output
- `outputs/cleaned/cleaned_player_dataset.csv` — 353,422 rows × 39 columns

---

## Stage 4: Enriching (Feature Engineering)

**Objective**: Create derived features based on cleaned data (fix issue #3).

### 4.1 Per-90 Efficiency Features
```
goals_per_90 = (goals / minutes_played) * 90
assists_per_90 = (assists / minutes_played) * 90
goal_contributions_per_90 = ((goals + assists) / minutes_played) * 90
yellow_cards_per_90 = (yellow_cards / minutes_played) * 90
clean_sheets_per_90 = (clean_sheets / minutes_played) * 90
goals_conceded_per_90 = (goals_conceded / minutes_played) * 90
```
- When denominator is 0, set to 0.0 (not NaN/inf)

### 4.2 Age Features (fix issue #10)
```
age_squared = age ** 2
career_stage = cut(age, [0,21,24,28,32,50], labels=[youth/emerging/prime/experienced/veteran])
```

### 4.3 Market Value Change (fix issue #6)
```
market_value_change = market_value - market_value_start
market_value_change_pct = market_value_change / market_value_start  (where start > 0)
```
- **log_market_value is NOT created** — log transformation should be applied at the modeling stage as needed

### 4.4 Injury Features
```
injury_severity = total_days_missed / injury_count  (where injury_count > 0, else 0)
was_injured = (injury_count > 0)
```

### 4.5 International Career Features
```
intl_goals_per_cap = intl_goals / intl_caps  (where caps > 0, else 0)
has_intl_career = (intl_caps > 0)
```

### 4.6 League Encoding (fix issue #9)
- `league_tier`: Extracted from trailing digits of competition_id (GB1 → 1, GB2 → 2)
- `is_top_division`: league_tier == 1
- Big-5 league binary flags: `is_GB1, is_ES1, is_IT1, is_L1, is_FR1`
- **No ordinal encoding over 1,400+ league codes**

### 4.8 Position Encoding
- One-Hot: `pos_Defender, pos_Midfield, pos_Attack` (Goalkeeper as baseline)

### 4.9 Excluded Features
- **fee_to_value_ratio**: NOT created (97.67% missing, issue #8)
- **log_market_value**: NOT created (data leakage risk, issue #6)

### 4.10 Post-Enrichment Validation
- Verified no inf/-inf in per_90 columns
- Verified age_squared == age ** 2
- Verified market_value was not modified during enrichment
- Verified log_market_value and fee_to_value_ratio do not exist

### Outputs
- `enriched_player_dataset.csv` — 353,422 rows × 63 columns (with identifiers, for EDA)
- `enriched_modeling_ready.csv` — 353,422 rows × 50 columns (with player_id + numeric/encoded columns + target variable, for modeling)

---

## 13 Issues — Fix Status

| # | Issue | Fix Location | Status |
|---|-------|-------------|--------|
| 1 | age not computed from DOB | Stage 2.9 | ✅ age missing = 0 |
| 2 | market_value only used latest table | Stage 2.3 | ✅ Full history + season start/end values |
| 3 | Feature engineering before cleaning | run_pipeline order | ✅ Stage 3 → Stage 4 |
| 4 | Overly aggressive IQR clipping on goals/assists | Stage 3.4 | ✅ Replaced with domain-knowledge caps |
| 5 | market_value was clipped | Stage 3.4 | ✅ No clipping, max = 200,000,000 |
| 6 | log_market_value leakage | Stage 4.9 | ✅ Not created |
| 7 | Useful features discarded | Stage 2 throughout | ✅ Retained injury/international/transfer/league data |
| 8 | fee_to_value_ratio useless | Stage 4.9 | ✅ Not created |
| 9 | League ordinal encoding | Stage 4.6 | ✅ Replaced with tier + big-5 flags |
| 10 | Age-derived features invalid | Stage 4.2 | ✅ Age now fully populated |
| 11 | Non-group-aware imputation | Stage 3.3 | ✅ Group-median imputation |
| 12 | Empty-shell rows not filtered | Stage 2.10 | ✅ Filtered NaN + zero market_value |
| 13 | player_id stored as float | Stage 3.1 | ✅ Converted to Int64 |

---

## Additional Issues Discovered and Fixed During Implementation

| Issue | Fix |
|-------|-----|
| modeling_ready.csv was missing player_id | Removed player_id from the drop list in Stage 4 |
| player_name had `(id)` suffix, e.g. `Messi (28003)` | Stage 3.5: cleaned with regex `\s*\(\d+\)\s*$` |
| position and main_position became identical after standardization | position now preserves original 17 sub-categories; main_position standardized to 4 broad categories |
| 22,679 rows with market_value == 0 have no modeling value | Stage 2.10: filtered alongside NaN rows |
| minutes_played=0 but goals/assists>0 — data contradiction | Stage 3.3b: zeroed all performance stats for contradictory rows |

---

## Final Output Schema

### enriched_player_dataset.csv (63 columns)

```
# Identifiers
player_id, player_name, season

# Player Attributes
age, height, citizenship, is_eu, position, main_position, foot

# Match Performance
goals, assists, own_goals, minutes_played, yellow_cards, red_cards,
clean_sheets, goals_conceded, appearances, penalty_goals, num_teams

# Target Variable
market_value, market_value_start

# Injuries
injury_count, total_days_missed, total_games_missed, max_single_injury_days

# International
intl_caps, intl_goals

# Team Context
primary_team_id, primary_team_name, competition_id, competition_name, club_division

# Transfers
num_transfers, total_transfer_fee, max_transfer_fee, had_loan, ds_b_league

# Derived: Efficiency
goals_per_90, assists_per_90, goal_contributions_per_90,
yellow_cards_per_90, clean_sheets_per_90, goals_conceded_per_90

# Derived: Age
age_squared, career_stage

# Derived: Market Value Change
market_value_change, market_value_change_pct

# Derived: Injury
injury_severity, was_injured

# Derived: International
intl_goals_per_cap, has_intl_career

# Derived: League
league_tier, is_top_division, is_GB1, is_ES1, is_IT1, is_L1, is_FR1

# Derived: Position One-Hot
pos_Defender, pos_Midfield, pos_Attack
```

### enriched_modeling_ready.csv (50 columns)
Same as above but excludes: player_name, season, citizenship, primary_team_name, competition_name, club_division, ds_b_league, is_eu, position, main_position, foot, career_stage, competition_id. Retains player_id as row identifier.
