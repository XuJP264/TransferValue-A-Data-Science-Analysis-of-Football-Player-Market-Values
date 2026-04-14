# Unified Player-Level Dataset Schema

## Target Variable

market_value

## Entity

Player-season level dataset

## Proposed schema

| Column | Description | Source Dataset |
|---|---|---|
| player_id | Stable player identifier for joins | Dataset A (datalake/transfermarkt/player_injuries/player_injuries.csv) |
| player_name | Player name | Dataset A (datalake/transfermarkt/player_profiles/player_profiles.csv) |
| season | Season of observation | Dataset A (datalake/transfermarkt/player_injuries/player_injuries.csv) |
| age | Player age in season/transfer window | Dataset B (dataset/transfers.csv) |
| position | Primary playing position | Dataset A (datalake/transfermarkt/player_profiles/player_profiles.csv) |
| team_id | Team/club identifier | Dataset A (datalake/transfermarkt/player_national_performances/player_national_performances.csv) |
| team_name | Team/club name | Dataset A (datalake/transfermarkt/player_performances/player_performances.csv) |
| league | League or competition context | Dataset A (datalake/transfermarkt/player_performances/player_performances.csv) |
| goals | Goals scored (aggregated player-season) | Dataset A (player_performances expected) |
| assists | Assists (aggregated player-season) | Dataset A (player_performances expected) |
| minutes_played | Minutes played (aggregated player-season) | Dataset A (player_performances expected) |
| transfer_fee | Transfer fee amount | Dataset A (datalake/transfermarkt/transfer_history/transfer_history.csv) |
| market_value | Observed market value | Dataset A (datalake/transfermarkt/player_latest_market_value/player_latest_market_value.csv) |

## Feature categories

- Player attributes
- Performance metrics
- Team context
- Transfer market information

## Notes

The unified schema is designed for downstream structuring and modeling. At this stage it is a target design, not a cleaned production table.
