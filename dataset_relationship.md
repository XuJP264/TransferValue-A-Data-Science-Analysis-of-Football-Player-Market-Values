# Dataset Relationship Analysis

## Dataset A
Comprehensive Transfermarkt-style football datalake with player profiles, performances, market values, injuries, transfers, and team context.

Representative files:
- `datalake/transfermarkt/player_latest_market_value/player_latest_market_value.csv` (69441 rows, 3 columns)
- `datalake/transfermarkt/player_market_value/player_market_value.csv` (901429 rows, 3 columns)
- `datalake/transfermarkt/player_performances/player_performances.csv` (1878719 rows, 20 columns)

## Dataset B
European transfer-market dataset centered on transfer transactions, transfer fees, market values at transfer, and league-season metadata.

Representative files:
- `dataset/transfers.csv` (70006 rows, 23 columns)
- `data/ES1_2009_s.json` (1 rows, 20 columns)
- `data/ES1_2009_w.json` (1 rows, 18 columns)

## Dataset C
Repository `Modelling-Football-Players-Values-on-a-Transfer-Market` includes additional structured data potentially used for player value modeling and feature engineering.

Representative files:
- `transfermarkt_fbref_201718.csv` (2232 rows, 400 columns)
- `transfermarkt_fbref_201819.csv` (2232 rows, 400 columns)
- `transfermarkt_fbref_201920.csv` (2644 rows, 400 columns)

## Potential Join Keys

| Dataset A/File | Dataset B or C/File | Join Key | Left Column | Right Column |
|---|---|---|---|---|
| Dataset A / datalake/transfermarkt/player_latest_market_value/player_latest_market_value.csv | Dataset B / dataset/transfers.csv | player_id | player_id | player_id |
| Dataset A / datalake/transfermarkt/player_market_value/player_market_value.csv | Dataset B / dataset/transfers.csv | player_id | player_id | player_id |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset B / dataset/transfers.csv | league | competition_id | league |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset B / dataset/transfers.csv | player_id | player_id | player_id |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset B / dataset/transfers.csv | season | season_name | season |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset B / dataset/transfers.csv | team_id | team_id | team_id |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset B / dataset/transfers.csv | team_name | team_name | team_name |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset B / dataset/transfers.csv | player_id | player_id | player_id |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset B / dataset/transfers.csv | player_name | player_name | player_name |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset B / dataset/transfers.csv | position | position | player_pos |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset B / dataset/transfers.csv | team_id | current_club_id | team_id |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset B / dataset/transfers.csv | team_name | current_club_name | team_name |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset B / dataset/transfers.csv | league | competition_id | league |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset B / dataset/transfers.csv | season | season_id | season |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset B / dataset/transfers.csv | team_id | club_id | team_id |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset B / dataset/transfers.csv | team_name | team_name | team_name |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset C / transfermarkt_fbref_201718.csv | league | competition_id | league |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset C / transfermarkt_fbref_201718.csv | season | season_name | Season |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset C / transfermarkt_fbref_201819.csv | league | competition_id | league |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset C / transfermarkt_fbref_201819.csv | season | season_name | Season |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset C / transfermarkt_fbref_201920.csv | league | competition_id | league |
| Dataset A / datalake/transfermarkt/player_performances/player_performances.csv | Dataset C / transfermarkt_fbref_201920.csv | season | season_name | Season |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset C / transfermarkt_fbref_201718.csv | player_name | player_name | player |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset C / transfermarkt_fbref_201718.csv | position | position | position |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset C / transfermarkt_fbref_201819.csv | player_name | player_name | player |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset C / transfermarkt_fbref_201819.csv | position | position | position |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset C / transfermarkt_fbref_201920.csv | player_name | player_name | player |
| Dataset A / datalake/transfermarkt/player_profiles/player_profiles.csv | Dataset C / transfermarkt_fbref_201920.csv | position | position | position |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset C / transfermarkt_fbref_201718.csv | league | competition_id | league |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset C / transfermarkt_fbref_201718.csv | season | season_id | Season |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset C / transfermarkt_fbref_201819.csv | league | competition_id | league |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset C / transfermarkt_fbref_201819.csv | season | season_id | Season |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset C / transfermarkt_fbref_201920.csv | league | competition_id | league |
| Dataset A / datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | Dataset C / transfermarkt_fbref_201920.csv | season | season_id | Season |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201718.csv | age | player_age | age |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201718.csv | league | league | league |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201718.csv | player_name | player_name | player |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201718.csv | position | player_pos | position |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201718.csv | season | season | Season |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201819.csv | age | player_age | age |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201819.csv | league | league | league |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201819.csv | player_name | player_name | player |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201819.csv | position | player_pos | position |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201819.csv | season | season | Season |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201920.csv | age | player_age | age |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201920.csv | league | league | league |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201920.csv | player_name | player_name | player |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201920.csv | position | player_pos | position |
| Dataset B / dataset/transfers.csv | Dataset C / transfermarkt_fbref_201920.csv | season | season | Season |
## Possible Integration Strategy

1. Use Dataset A player-level tables as the primary backbone because they contain player identifiers, market values, profiles, and performance history.
2. Join Dataset B transfers on `player_id` and `season` where available, and use `player_name` as a fallback key with careful standardization.
3. Align team context using `team_id` / `team_name` and season context for transfer windows.
4. Incorporate Dataset C tabular files if present; otherwise treat Dataset C as methodological reference for modeling choices and engineered features.
5. Build a player-season analytical mart with one record per player-season and aggregated metrics from performances, transfer events, and market value observations.
