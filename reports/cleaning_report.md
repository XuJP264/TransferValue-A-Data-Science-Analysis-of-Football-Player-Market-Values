# Data Cleaning Report

## Input and Output

- Input file: `D:\PythonProject\TransferValue\enriched_data\enriched_player_dataset.csv`
- Output file: `D:\PythonProject\TransferValue\cleaned_data\cleaned_player_dataset.csv`
- Rows before cleaning: 801157
- Rows after cleaning: 797262
- Columns before cleaning: 20
- Columns after cleaning: 20

## Operations Applied

- Exact duplicates removed: 0
- Rows dropped for missing core keys (player_name, season): 3895
- Object columns converted to numeric: None
- Categorical normalization applied to: player_name, position, team_name, league

## Missing Value Handling

- player_id: left unchanged (0.82% missing, identifier-like column)
- age: left unchanged (93.76% missing, high missingness)
- goals: median imputation applied (6.78% missing)
- assists: median imputation applied (1.29% missing)
- minutes: left unchanged (39.92% missing, high missingness)
- transfer_fee: left unchanged (97.33% missing, high missingness)
- market_value: left unchanged (43.32% missing, high missingness)
- goals_per_90: left unchanged (45.42% missing, high missingness)
- assists_per_90: left unchanged (39.92% missing, high missingness)
- goal_contribution_per_90: left unchanged (45.42% missing, high missingness)
- age_squared: left unchanged (93.76% missing, high missingness)
- fee_to_value_ratio: left unchanged (97.67% missing, high missingness)
- log_market_value: left unchanged (43.32% missing, high missingness)
- position: filled with 'Unknown' (0.00% missing)


## Outlier Handling

- market_value: winsorized with IQR bounds [-950000.0000, 1850000.0000], lower_clipped=0, upper_clipped=61499
- transfer_fee: winsorized with IQR bounds [-3000000.0000, 5000000.0000], lower_clipped=0, upper_clipped=2583
- goals: winsorized with IQR bounds [-4.5000, 7.5000], lower_clipped=0, upper_clipped=61705
- assists: winsorized with IQR bounds [-1.5000, 2.5000], lower_clipped=0, upper_clipped=117353
- minutes: winsorized with IQR bounds [-1064.5000, 2619.5000], lower_clipped=0, upper_clipped=27167


## Columns Affected

- assists, goals, league, market_value, minutes, player_name, position, season, team_name, transfer_fee

## Justification

- Cleaning used conservative operations to avoid removing large portions of data.
- High-missingness columns were left unchanged when imputation risked distortion.
- IQR winsorization was preferred over row deletion to preserve sample size.
