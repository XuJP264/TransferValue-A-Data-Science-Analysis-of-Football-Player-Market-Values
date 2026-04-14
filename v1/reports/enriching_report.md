# Data Enriching Report

## Input

- Input file: `D:\PythonProject\TransferValue\structured_data\unified_player_dataset.csv`
- Input shape: (801157, 12)

## Numeric Detection

- Numeric columns detected after auto-conversion: 7
- Object columns auto-converted to numeric: None

## New Features Created

| Feature | Formula | Input Columns |
|---|---|---|
| goals_per_90 | (goals / minutes) * 90 | goals, minutes |
| assists_per_90 | (assists / minutes) * 90 | assists, minutes |
| goal_contribution_per_90 | ((goals + assists) / minutes) * 90 | goals, assists, minutes |
| age_squared | age ** 2 | age |
| career_stage | young if age<24, prime if 24<=age<=30, veteran if age>30, else unknown | age |
| fee_to_value_ratio | transfer_fee / market_value | transfer_fee, market_value |
| log_market_value | log1p(market_value) when market_value>=0 | market_value |
| league_encoded | categorical integer code from league labels | league |

## Skipped Features

- minutes_per_game (no game/match/appearance column detected)


## Output

- Output file: `D:\PythonProject\TransferValue\enriched_data\enriched_player_dataset.csv`
- Output shape: (801157, 20)
