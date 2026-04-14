# Data Profiling Report (v2 Pipeline)

## player_id Type Consistency

All tables have `player_id` as `int64` ✓

## File Summaries

### player_performances.csv

- **Status**: OK
- **Rows**: 1,878,719
- **Columns**: 20
- **Columns**: player_id, season_name, competition_id, competition_name, team_id, team_name, nb_in_group, nb_on_pitch, goals, assists, own_goals, subed_in, subed_out, yellow_cards, second_yellow_cards, direct_red_cards, penalty_goals, minutes_played, goals_conceded, clean_sheets
- **Top missing columns**:
  - `minutes_played`: 62.3%
  - `goals`: 7.4%
- **player_id dtype**: `int64`

### player_profiles.csv

- **Status**: OK
- **Rows**: 92,671
- **Columns**: 34
- **Columns**: player_id, player_slug, player_name, player_image_url, name_in_home_country, date_of_birth, place_of_birth, country_of_birth, height, citizenship, is_eu, position, main_position, foot, current_club_id, current_club_name, joined, contract_expires, outfitter, social_media_url, player_agent_id, player_agent_name, contract_option, date_of_last_contract_extension, on_loan_from_club_id, on_loan_from_club_name, contract_there_expires, second_club_url, second_club_name, third_club_url, third_club_name, fourth_club_url, fourth_club_name, date_of_death
- **Top missing columns**:
  - `fourth_club_url`: 100.0%
  - `fourth_club_name`: 100.0%
  - `third_club_url`: 100.0%
  - `third_club_name`: 100.0%
  - `date_of_death`: 99.7%
  - `second_club_url`: 98.9%
  - `second_club_name`: 98.9%
  - `contract_there_expires`: 97.3%
  - `contract_option`: 96.2%
  - `on_loan_from_club_id`: 95.9%
- **player_id dtype**: `int64`

### player_market_value.csv

- **Status**: OK
- **Rows**: 901,429
- **Columns**: 3
- **Columns**: player_id, date_unix, value
- **player_id dtype**: `int64`

### player_injuries.csv

- **Status**: OK
- **Rows**: 143,195
- **Columns**: 7
- **Columns**: player_id, season_name, injury_reason, from_date, end_date, days_missed, games_missed
- **Top missing columns**:
  - `end_date`: 1.1%
  - `from_date`: 0.0%
  - `days_missed`: 0.0%
- **player_id dtype**: `int64`

### player_national_performances.csv

- **Status**: OK
- **Rows**: 92,701
- **Columns**: 9
- **Columns**: player_id, team_id, matches, goals, shirt_number, debut, coach_id, debut_game_id, career_state
- **Top missing columns**:
  - `debut`: 100.0%
  - `coach_id`: 39.8%
  - `debut_game_id`: 32.7%
- **player_id dtype**: `int64`

### team_competitions_seasons.csv

- **Status**: OK
- **Rows**: 196,378
- **Columns**: 7
- **Columns**: club_id, team_name, season_id, competition_name, competition_id, club_division, _last_modified_at
- **Top missing columns**:
  - `competition_name`: 16.4%
  - `competition_id`: 16.4%
  - `club_division`: 16.4%

### transfer_history.csv

- **Status**: OK
- **Rows**: 1,101,440
- **Columns**: 10
- **Columns**: player_id, season_name, transfer_date, from_team_id, from_team_name, to_team_id, to_team_name, transfer_type, value_at_transfer, transfer_fee
- **Top missing columns**:
  - `transfer_date`: 0.1%
- **player_id dtype**: `int64`

### transfers.csv

- **Status**: OK
- **Rows**: 70,006
- **Columns**: 23
- **Columns**: league, season, window, team_id, team_name, team_country, dir, player_id, player_name, player_age, player_nation, player_nation2, player_pos, counter_team_id, counter_team_name, counter_team_country, transfer_fee_amnt, market_val_amnt, is_free, is_loan, is_loan_end, is_retired, transfer_id
- **Top missing columns**:
  - `player_nation2`: 66.9%
  - `transfer_fee_amnt`: 59.6%
  - `market_val_amnt`: 27.5%
  - `player_age`: 0.0%
  - `player_nation`: 0.0%
- **player_id dtype**: `int64`
