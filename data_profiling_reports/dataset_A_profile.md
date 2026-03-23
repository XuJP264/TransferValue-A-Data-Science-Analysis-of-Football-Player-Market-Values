# Dataset A Profiling Report

## Dataset overview

- Dataset path: `D:\PythonProject\TransferValue\football-datasets`
- Number of files: 11
- Total dataset size: 349.237 MB
- Total memory usage (loaded tables): 204.377 MB

## File structure

- `datalake/transfermarkt/player_injuries/player_injuries.csv` (7.815 MB)
- `datalake/transfermarkt/player_latest_market_value/player_latest_market_value.csv` (1.667 MB)
- `datalake/transfermarkt/player_market_value/player_market_value.csv` (23.627 MB)
- `datalake/transfermarkt/player_national_performances/player_national_performances.csv` (4.928 MB)
- `datalake/transfermarkt/player_performances/player_performances.csv` (150.344 MB) [sampled first 10k rows]
- `datalake/transfermarkt/player_profiles/player_profiles.csv` (25.247 MB) [sampled first 10k rows]
- `datalake/transfermarkt/player_teammates_played_with/player_teammates_played_with.csv` (46.695 MB) [sampled first 10k rows]
- `datalake/transfermarkt/team_children/team_children.csv` (0.494 MB)
- `datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv` (10.521 MB)
- `datalake/transfermarkt/team_details/team_details.csv` (0.583 MB)
- `datalake/transfermarkt/transfer_history/transfer_history.csv` (77.314 MB) [sampled first 10k rows]

## Dataset-level profiling

| Table | Rows | Columns | File Size (MB) | Memory Usage (MB) | Sampled | Load Error |
| --- | --- | --- | --- | --- | --- | --- |
| datalake/transfermarkt/player_injuries/player_injuries.csv | 143195 | 7 | 7.815 | 39.639 | No | No |
| datalake/transfermarkt/player_latest_market_value/player_latest_market_value.csv | 69441 | 3 | 1.667 | 5.497 | No | No |
| datalake/transfermarkt/player_market_value/player_market_value.csv | 901429 | 3 | 23.627 | 71.353 | No | No |
| datalake/transfermarkt/player_national_performances/player_national_performances.csv | 92701 | 9 | 4.928 | 12.646 | No | No |
| datalake/transfermarkt/player_performances/player_performances.csv | 1878719 | 20 | 150.344 | 3.820 | Yes | No |
| datalake/transfermarkt/player_profiles/player_profiles.csv | 92671 | 34 | 25.247 | 13.771 | Yes | No |
| datalake/transfermarkt/player_teammates_played_with/player_teammates_played_with.csv | 1257342 | 6 | 46.695 | 1.095 | Yes | No |
| datalake/transfermarkt/team_children/team_children.csv | 7695 | 5 | 0.494 | 1.813 | No | No |
| datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv | 58247 | 29 | 10.521 | 49.425 | No | No |
| datalake/transfermarkt/team_details/team_details.csv | 2175 | 12 | 0.583 | 1.726 | No | No |
| datalake/transfermarkt/transfer_history/transfer_history.csv | 1101440 | 10 | 77.314 | 3.591 | Yes | No |

## Table-level profiling

### Table: `datalake/transfermarkt/player_injuries/player_injuries.csv`

- Rows: 143195
- Columns: 7
- Duplicate rows: 111
- Duplicate row percentage: 0.08%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| player_id | int64 | 0 | 0.00% | 34561 | 2.0000 | 1396965.0000 | 253159.2909 | 231876.6084 | 10 (15); 186233 (15); 183309 (15); 183318 (15); 183321 (15) |
| season_name | object | 0 | 0.00% | 46 |  |  |  |  | 24/25 (15102); 21/22 (14885); 23/24 (14483); 22/23 (14296); 20/21 (14058) |
| injury_reason | object | 0 | 0.00% | 349 |  |  |  |  | unknown injury (27028); Muscle injury (6433); Hamstring injury (5786); Knee injury (5544); muscular problems (4880) |
| from_date | object | 22 | 0.02% | 8133 |  |  |  |  | 2021-04-01 (204); 2023-08-01 (129); 2019-08-01 (127); 2022-09-01 (126); 2025-02-20 (126) |
| end_date | object | 1523 | 1.06% | 8114 |  |  |  |  | NaN (1523); 2024-06-30 (404); 2023-06-30 (380); 2025-06-30 (319); 2022-06-30 (309) |
| days_missed | float64 | 22 | 0.02% | 866 | 1.0000 | 8655.0000 | 51.7193 | 104.4372 | 8.0 (6980); 5.0 (5270); 15.0 (5000); 6.0 (4449); 7.0 (4306) |
| games_missed | int64 | 0 | 0.00% | 135 | 0.0000 | 208.0000 | 6.6285 | 9.4684 | 1 (30544); 2 (21631); 3 (15502); 4 (11920); 5 (8938) |

#### Multi-column profiling

- Candidate primary keys: None detected
- Columns with >50% missing values: None
- Possible join keys: player_id: [player_id]; season: [season_name]

- High correlation pairs (|r|>=0.8): None

### Table: `datalake/transfermarkt/player_latest_market_value/player_latest_market_value.csv`

- Rows: 69441
- Columns: 3
- Duplicate rows: 0
- Duplicate row percentage: 0.00%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| player_id | int64 | 0 | 0.00% | 69441 | 1.0000 | 1407924.0000 | 388128.4774 | 329398.7610 | 1 (1); 714494 (1); 712093 (1); 712100 (1); 712141 (1) |
| date_unix | object | 0 | 0.00% | 4802 |  |  |  |  | 2025-06-24 (2369); 2025-06-18 (2210); 2025-05-14 (1874); 2025-06-17 (1829); 2022-10-03 (1790) |
| value | float64 | 0 | 0.00% | 125 | 0.0000 | 200000000.0000 | 761318.6374 | 4342874.3928 | 0.0 (35851); 100000.0 (2919); 50000.0 (2768); 200000.0 (2452); 150000.0 (2229) |

#### Multi-column profiling

- Candidate primary keys: player_id
- Columns with >50% missing values: None
- Possible join keys: player_id: [player_id]

- High correlation pairs (|r|>=0.8): None

### Table: `datalake/transfermarkt/player_market_value/player_market_value.csv`

- Rows: 901429
- Columns: 3
- Duplicate rows: 0
- Duplicate row percentage: 0.00%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| player_id | int64 | 0 | 0.00% | 69441 | 1.0000 | 1407924.0000 | 277556.9251 | 255153.7103 | 39333 (55); 44162 (54); 57162 (53); 18829 (53); 39153 (53) |
| date_unix | object | 0 | 0.00% | 6871 |  |  |  |  | 2020-04-07 (12918); 2004-10-03 (6572); 2015-06-30 (4912); 2023-12-20 (3864); 2023-12-19 (3842) |
| value | float64 | 0 | 0.00% | 486 | 0.0000 | 200000000.0000 | 1544902.9112 | 5424064.6614 | 50000.0 (67404); 100000.0 (64575); 200000.0 (55567); 150000.0 (49011); 0.0 (48009) |

#### Multi-column profiling

- Candidate primary keys: None detected
- Columns with >50% missing values: None
- Possible join keys: player_id: [player_id]

- High correlation pairs (|r|>=0.8): None

### Table: `datalake/transfermarkt/player_national_performances/player_national_performances.csv`

- Rows: 92701
- Columns: 9
- Duplicate rows: 32
- Duplicate row percentage: 0.03%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| player_id | int64 | 0 | 0.00% | 36339 | 1.0000 | 1428280.0000 | 282054.2096 | 283391.8146 | 909853 (14); 387191 (10); 295060 (10); 744199 (10); 503975 (10) |
| team_id | int64 | 0 | 0.00% | 1108 | 3262.0000 | 134572.0000 | 21036.9998 | 13565.5683 | 21746 (839); 21100 (760); 21426 (754); 23133 (728); 16371 (681) |
| matches | int64 | 0 | 0.00% | 166 | 0.0000 | 223.0000 | 7.3360 | 12.9431 | 1 (13346); 0 (12062); 2 (11235); 3 (9232); 4 (6995) |
| goals | int64 | 0 | 0.00% | 73 | 0.0000 | 141.0000 | 0.9114 | 2.9102 | 0 (65322); 1 (12575); 2 (5484); 3 (3018); 4 (1755) |
| shirt_number | int64 | 0 | 0.00% | 56 | 0.0000 | 255.0000 | 4.7585 | 6.9699 | 0 (52915); 10 (2348); 9 (2242); 11 (2209); 7 (2088) |
| debut | float64 | 92701 | 100.00% | 0 |  |  |  |  | NaN (92701) |
| coach_id | float64 | 36922 | 39.83% | 3117 | 2.0000 | 147663.0000 | 18948.8133 | 21337.1076 | NaN (36922); 2274.0 (359); 11925.0 (331); 18420.0 (316); 5629.0 (315) |
| debut_game_id | float64 | 30347 | 32.74% | 20163 | 263.0000 | 4729550.0000 | 2864735.8804 | 956691.5647 | NaN (30347); 2371883.0 (302); 982113.0 (273); 2365994.0 (232); 2983370.0 (231) |
| career_state | object | 0 | 0.00% | 4 |  |  |  |  | FORMER_NATIONAL_PLAYER (85816); CURRENT_NATIONAL_PLAYER (2936); RECENT_NATIONAL_PLAYER (2475); RETIRED_NATIONAL_PLAYER (1474) |

#### Multi-column profiling

- Candidate primary keys: None detected
- Columns with >50% missing values: debut
- Possible join keys: player_id: [player_id]; team_id: [team_id]

- High correlation pairs (|r|>=0.8): None

### Table: `datalake/transfermarkt/player_performances/player_performances.csv`

- Rows: 10000
- Columns: 20
- Duplicate rows: 0
- Duplicate row percentage: 0.00%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| player_id | int64 | 0 | 0.00% | 728 | 1.0000 | 1013774.0000 | 493792.6221 | 468722.6749 | 101294 (88); 10055 (81); 100091 (73); 100750 (71); 100136 (71) |
| season_name | object | 0 | 0.00% | 76 |  |  |  |  | 24/25 (937); 23/24 (818); 22/23 (717); 2024 (470); 21/22 (453) |
| competition_id | object | 0 | 0.00% | 740 |  |  |  |  | CGB (235); FAC (225); MNP3 (223); BRC (195); TRP (186) |
| competition_name | object | 0 | 0.00% | 880 |  |  |  |  | FA Cup (225); MLS Next Pro (223); Copa do Brasil (195); Türkiye Kupasi (186); League Cup (182) |
| team_id | int64 | 0 | 0.00% | 1825 | 1.0000 | 122308.0000 | 14495.4205 | 23291.9688 | 703 (140); 199 (92); 990 (91); 6692 (83); 5 (82) |
| team_name | object | 0 | 0.00% | 1889 |  |  |  |  | Nottingham Forest (140); Sport Club Corinthians Paulista (92); Coventry City (91); AC Milan (82); Novara Calcio 1908 (82) |
| nb_in_group | int64 | 0 | 0.00% | 46 | 1.0000 | 46.0000 | 9.0100 | 10.0506 | 1 (2171); 2 (1556); 3 (834); 4 (690); 5 (398) |
| nb_on_pitch | int64 | 0 | 0.00% | 47 | 0.0000 | 46.0000 | 7.2817 | 9.1560 | 1 (2057); 2 (1373); 0 (1222); 3 (763); 4 (569) |
| goals | float64 | 796 | 7.96% | 26 | 0.0000 | 26.0000 | 0.8724 | 2.1365 | 0.0 (6437); 1.0 (1242); NaN (796); 2.0 (559); 3.0 (294) |
| assists | int64 | 0 | 0.00% | 15 | 0.0000 | 15.0000 | 0.3332 | 1.0328 | 0 (8367); 1 (912); 2 (330); 3 (169); 4 (86) |
| own_goals | int64 | 0 | 0.00% | 3 | 0.0000 | 2.0000 | 0.0121 | 0.1129 | 0 (9883); 1 (113); 2 (4) |
| subed_in | int64 | 0 | 0.00% | 27 | 0.0000 | 28.0000 | 1.6214 | 2.9569 | 0 (5315); 1 (1913); 2 (751); 3 (473); 4 (354) |
| subed_out | int64 | 0 | 0.00% | 26 | 0.0000 | 25.0000 | 1.6961 | 3.0564 | 0 (5272); 1 (1805); 2 (819); 3 (507); 4 (341) |
| yellow_cards | int64 | 0 | 0.00% | 16 | 0.0000 | 17.0000 | 0.9449 | 1.7569 | 0 (6201); 1 (1750); 2 (735); 3 (485); 4 (278) |
| second_yellow_cards | int64 | 0 | 0.00% | 4 | 0.0000 | 3.0000 | 0.0286 | 0.1777 | 0 (9732); 1 (251); 2 (16); 3 (1) |
| direct_red_cards | int64 | 0 | 0.00% | 4 | 0.0000 | 3.0000 | 0.0310 | 0.1840 | 0 (9706); 1 (281); 2 (10); 3 (3) |
| penalty_goals | int64 | 0 | 0.00% | 9 | 0.0000 | 8.0000 | 0.0553 | 0.3661 | 0 (9671); 1 (211); 2 (60); 3 (31); 5 (12) |
| minutes_played | float64 | 6440 | 64.40% | 1152 | 5.0000 | 4140.0000 | 552.1048 | 638.0230 | NaN (6440); 90.0 (233); 180.0 (142); 270.0 (77); 360.0 (64) |
| goals_conceded | int64 | 0 | 0.00% | 56 | 0.0000 | 65.0000 | 0.7815 | 4.2196 | 0 (9253); 2 (102); 1 (95); 3 (89); 4 (53) |
| clean_sheets | int64 | 0 | 0.00% | 21 | 0.0000 | 20.0000 | 0.1724 | 1.1006 | 0 (9547); 1 (141); 2 (95); 3 (47); 4 (43) |

#### Multi-column profiling

- Candidate primary keys: None detected
- Columns with >50% missing values: minutes_played
- Possible join keys: player_id: [player_id]; team_id: [team_id]; competition_id: [competition_id]; season: [season_name]

| Column 1 | Column 2 | Correlation (|r|>=0.8) |
| --- | --- | --- |
| nb_in_group | nb_on_pitch | 0.9308 |

### Table: `datalake/transfermarkt/player_profiles/player_profiles.csv`

- Rows: 10000
- Columns: 34
- Duplicate rows: 0
- Duplicate row percentage: 0.00%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| player_id | int64 | 0 | 0.00% | 10000 | 1.0000 | 1372119.0000 | 822903.7628 | 463394.9456 | 1 (1); 1076671 (1); 1076584 (1); 1076386 (1); 1076589 (1) |
| player_slug | object | 0 | 0.00% | 9849 |  |  |  |  | dudu (7); robinho (5); juninho (4); kauan (4); jorginho (4) |
| player_name | object | 56 | 0.56% | 9944 |  |  |  |  | NaN (56); Silvio Adzic (1) (1); Furkan Çiftçi (1076674) (1); Bruno Faria (1076381) (1); Jan Mutavcic (1076425) (1) |
| player_image_url | object | 0 | 0.00% | 3926 |  |  |  |  | https://img.a.transfermarkt.technology/portrait/header/default.jpg (6075); https://img.a.transfermarkt.technology/portrait/header/1-1465832419.jpg (1); https://img.a.transfermarkt.technology/portrait/header/1069931-1724076846.png (1); https://img.a.transfermarkt.technology/portrait/header/1069370-1746826175.jpg (1); https://img.a.transfermarkt.technology/portrait/header/1069459-1708556026.jpg (1) |
| name_in_home_country | object | 5286 | 52.86% | 4714 |  |  |  |  | NaN (5286); Souleymane Dioulde Diallo (1); Rahman Amarteye Addico Amartey (1); Finlay James Cartwright (1); Rhyan Bert Grant (1) |
| date_of_birth | object | 255 | 2.55% | 5252 |  |  |  |  | NaN (255); 2005-01-01 (19); 2004-01-01 (16); 2006-01-31 (15); 2003-01-01 (15) |
| place_of_birth | object | 3412 | 34.12% | 3213 |  |  |  |  | NaN (3412); London (75); Istanbul (68); Roma (67); São Paulo (52) |
| country_of_birth | object | 3414 | 34.14% | 155 |  |  |  |  | NaN (3414); Italy (874); France (666); Brazil (559); England (407) |
| height | float64 | 1 | 0.01% | 47 | 0.0000 | 204.0000 | 114.6975 | 87.7764 | 0.0 (3683); 180.0 (531); 178.0 (422); 183.0 (407); 185.0 (377) |
| citizenship | object | 5 | 0.05% | 833 |  |  |  |  | Italy (1563); Brazil (792); France (719); England (518); Türkiye (403) |
| is_eu | bool | 0 | 0.00% | 2 | 0.0000 | 1.0000 | 0.6790 | 0.4669 | True (6790); False (3210) |
| position | object | 1 | 0.01% | 17 |  |  |  |  | Defender - Centre-Back (1568); Attack - Centre-Forward (1200); Goalkeeper (1144); Midfield - Central Midfield (924); Midfield - Defensive Midfield (693) |
| main_position | object | 1 | 0.01% | 4 |  |  |  |  | Defender (3188); Midfield (3043); Attack (2624); Goalkeeper (1144); NaN (1) |
| foot | object | 3870 | 38.70% | 3 |  |  |  |  | right (4351); NaN (3870); left (1538); both (241) |
| current_club_id | int64 | 0 | 0.00% | 3548 | 2.0000 | 134304.0000 | 23292.0910 | 31941.7299 | 123 (1850); 515 (688); 75 (221); 11493 (27); 20406 (24) |
| current_club_name | object | 0 | 0.00% | 3546 |  |  |  |  | Retired (1850); Without Club (688); Unknown (221); Palermo Primavera (27); Reggiana Primavera (24) |
| joined | object | 669 | 6.69% | 1055 |  |  |  |  | 2025-07-01 (1597); 2024-07-01 (1010); NaN (669); 2023-07-01 (500); 2025-01-01 (241) |
| contract_expires | object | 5848 | 58.48% | 73 |  |  |  |  | NaN (5848); 2026-06-30 (1863); 2027-06-30 (559); 2025-12-31 (341); 2028-06-30 (297) |
| outfitter | object | 9673 | 96.73% | 20 |  |  |  |  | NaN (9673); Nike (123); adidas (118); Puma (48); Mizuno (10) |
| social_media_url | object | 8578 | 85.78% | 1422 |  |  |  |  | NaN (8578); http://www.instagram.com/_paraizo/ (1); http://www.instagram.com/souza0808/ (1); http://www.instagram.com/enesalbak/ (1); http://www.instagram.com/tahatosun1/ (1) |
| player_agent_id | float64 | 6461 | 64.61% | 1602 | 1.0000 | 14992.0000 | 6260.8861 | 4177.2501 | NaN (6461); 440.0 (70); 190.0 (61); 674.0 (56); 4142.0 (47) |
| player_agent_name | object | 6051 | 60.51% | 1599 |  |  |  |  | NaN (6051); Agent is known - Player under 18 (167); no agent (161); Relatives (81); Wasserman (70) |
| contract_option | object | 9672 | 96.72% | 15 |  |  |  |  | NaN (9672); club option 1 year (110); Option for a further year (67); Option to buy (48); club option 2 years (46) |
| date_of_last_contract_extension | object | 9081 | 90.81% | 455 |  |  |  |  | NaN (9081); 2025-07-01 (12); 2025-07-11 (12); 2025-07-08 (11); 2025-07-18 (9) |
| on_loan_from_club_id | float64 | 9358 | 93.58% | 481 | 5.0000 | 132806.0000 | 20570.5545 | 27818.1818 | NaN (9358); 3037.0 (4); 776.0 (4); 8492.0 (4); 15136.0 (4) |
| on_loan_from_club_name | object | 9358 | 93.58% | 481 |  |  |  |  | NaN (9358); Calcio Padova (4); Coritiba Foot Ball Club (4); Empoli Primavera (4); Vitória Guimarães SC B (4) |
| contract_there_expires | object | 9642 | 96.42% | 24 |  |  |  |  | NaN (9642); 2027-06-30 (103); 2028-06-30 (70); 2026-06-30 (41); 2026-12-31 (32) |
| second_club_url | object | 9638 | 96.38% | 215 |  |  |  |  | NaN (9638); /philadelphia-union-ii/startseite/verein/51762 (7); /us-sassuolo-uefa-u19/startseite/verein/122306 (6); /manchester-city-uefa-u19/startseite/verein/41593 (6); /juventus-turin-uefa-u19/startseite/verein/41592 (5) |
| second_club_name | object | 9638 | 96.38% | 323 |  |  |  |  | NaN (9638); Manchester City UEFA U19 (6); Arsenal FC UEFA U19 (4); Gil Vicente U23 (4); LKS Lodz II (3) |
| third_club_url | object | 9980 | 99.80% | 11 |  |  |  |  | NaN (9980); /krc-genk-uefa-u19/startseite/verein/76579 (4); /wuhan-three-towns-b/startseite/verein/125741 (3); /sporting-lissabon-uefa-u19/startseite/verein/45510 (3); /zaglebie-lubin-u19/startseite/verein/15535 (2) |
| third_club_name | object | 9980 | 99.80% | 16 |  |  |  |  | NaN (9980); Sporting Lissabon UEFA U19 (3); Zaglebie Lubin U19 (2); Bayern Munich UEFA U19 (2); Oud-Heverlee Leuven U18 (#12) (1) |
| fourth_club_url | float64 | 10000 | 100.00% | 0 |  |  |  |  | NaN (10000) |
| fourth_club_name | float64 | 10000 | 100.00% | 0 |  |  |  |  | NaN (10000) |
| date_of_death | object | 9976 | 99.76% | 24 |  |  |  |  | NaN (9976); 18.12.2023 (53) (1); 07.09.2024 (55) (1); 05.10.2021 (31) (1); 30.04.2015 (24) (1) |

#### Multi-column profiling

- Candidate primary keys: player_id
- Columns with >50% missing values: name_in_home_country, contract_expires, outfitter, social_media_url, player_agent_id, player_agent_name, contract_option, date_of_last_contract_extension, on_loan_from_club_id, on_loan_from_club_name, contract_there_expires, second_club_url, second_club_name, third_club_url, third_club_name, fourth_club_url, fourth_club_name, date_of_death
- Possible join keys: player_id: [player_id]; team_id: [current_club_id]; player_name: [player_name, name_in_home_country]

- High correlation pairs (|r|>=0.8): None

### Table: `datalake/transfermarkt/player_teammates_played_with/player_teammates_played_with.csv`

- Rows: 10000
- Columns: 6
- Duplicate rows: 0
- Duplicate row percentage: 0.00%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| player_id | int64 | 0 | 0.00% | 620 | 10.0000 | 1011692.0000 | 909342.4099 | 281996.2431 | 1008935 (25); 1004503 (25); 1004316 (25); 1009031 (25); 1005575 (25) |
| teammate_player_id | int64 | 0 | 0.00% | 7667 | 674.0000 | 1406626.0000 | 779120.8973 | 341714.0038 | 923832 (9); 1004619 (9); 1004618 (9); 954621 (9); 100074 (9) |
| teammate_player_name | object | 0 | 0.00% | 7539 |  |  |  |  | Dudu (11); Titouan Fortun (9); Nathan Zézé (9); Tom Mabon (9); Stredair Appuah (9) |
| ppg_played_with | float64 | 569 | 5.69% | 245 | 0.0800 | 3.0000 | 1.5533 | 0.5545 | NaN (569); 1.0 (414); 2.0 (399); 1.5 (381); 3.0 (300) |
| joint_goal_participation | float64 | 8974 | 89.74% | 12 | 1.0000 | 19.0000 | 1.6803 | 1.4983 | NaN (8974); 1.0 (687); 2.0 (191); 3.0 (68); 4.0 (32) |
| minutes_played_with | float64 | 3894 | 38.94% | 996 | 0.0000 | 999.0000 | 422.2979 | 299.2542 | NaN (3894); 90.0 (79); 0.0 (44); 44.0 (38); 20.0 (34) |

#### Multi-column profiling

- Candidate primary keys: None detected
- Columns with >50% missing values: joint_goal_participation
- Possible join keys: player_id: [player_id]

- High correlation pairs (|r|>=0.8): None

### Table: `datalake/transfermarkt/team_children/team_children.csv`

- Rows: 7695
- Columns: 5
- Duplicate rows: 0
- Duplicate row percentage: 0.00%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| parent_team_id | int64 | 0 | 0.00% | 1777 | 1.0000 | 132806.0000 | 10545.3214 | 17578.4552 | 935 (10); 141 (10); 368 (10); 467 (10); 35 (10) |
| parent_team_name | object | 0 | 0.00% | 1776 |  |  |  |  | CF Pachuca (10); FC St. Pauli (10); Lokomotiv Moscow (10); NEC Nijmegen (10); LASK Amateure OÖ (10) |
| child_team_id | int64 | 0 | 0.00% | 7608 | 1.0000 | 134550.0000 | 45771.9160 | 38933.2361 | 64328 (2); 59535 (2); 51663 (2); 7437 (2); 56870 (2) |
| child_team_name | object | 0 | 0.00% | 7607 |  |  |  |  | Atlanta United 2 (2); Académica Coimbra U19 (2); Atlanta United FC (2); LASK Linz JKU (2); Atlanta United Academy (2) |
| _last_modified_at | object | 0 | 0.00% | 1513 |  |  |  |  | 2025-09-13 09:41:55 (46); 2025-09-13 09:14:11 (43); 2025-09-13 09:04:14 (31); 2025-09-13 09:31:38 (28); 2025-09-13 09:14:12 (26) |

#### Multi-column profiling

- Candidate primary keys: None detected
- Columns with >50% missing values: None
- Possible join keys: None detected

- High correlation pairs (|r|>=0.8): None

### Table: `datalake/transfermarkt/team_competitions_seasons/team_competitions_seasons.csv`

- Rows: 58247
- Columns: 29
- Duplicate rows: 360
- Duplicate row percentage: 0.62%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| club_division | object | 0 | 0.00% | 10 |  |  |  |  | First Tier (27110); Second Tier (15816); Third Tier (7860); Fourth Tier (4352); Youth league (1610) |
| club_id | int64 | 0 | 0.00% | 2162 | 1.0000 | 133273.0000 | 6626.2958 | 13462.9769 | 29 (128); 405 (125); 289 (124); 762 (119); 31 (117) |
| competition_id | object | 0 | 0.00% | 356 |  |  |  |  | EFD1 (1918); IT2 (1858); IT1 (1676); ES1 (1618); ES2 (1596) |
| competition_name | object | 0 | 0.00% | 569 |  |  |  |  | First Division (- 91/92) (1918); Serie B (1858); Serie A (1676); LaLiga (1618); Segunda División (1552) |
| season_draws | int64 | 0 | 0.00% | 27 | 0.0000 | 26.0000 | 8.3664 | 3.9596 | 8 (5949); 9 (5715); 7 (5455); 10 (5225); 6 (4989) |
| season_goal_difference | int64 | 0 | 0.00% | 203 | -148.0000 | 196.0000 | 2.4696 | 19.4083 | 0 (1686); -2 (1612); -1 (1576); -4 (1521); -3 (1492) |
| season_goals_against | int64 | 0 | 0.00% | 126 | 0.0000 | 153.0000 | 40.7238 | 16.3584 | 40 (1532); 38 (1498); 39 (1492); 42 (1476); 43 (1451) |
| season_goals_for | int64 | 0 | 0.00% | 134 | 0.0000 | 213.0000 | 43.1934 | 17.5176 | 40 (1502); 39 (1467); 41 (1460); 42 (1458); 36 (1429) |
| season_id | int64 | 0 | 0.00% | 137 | 1888.0000 | 2025.0000 | 1997.3979 | 25.0344 | 2023 (1737); 2024 (1737); 2022 (1736); 2021 (1721); 2020 (1689) |
| season_is_two_point_system | bool | 0 | 0.00% | 2 | 0.0000 | 1.0000 | 0.2992 | 0.4579 | False (40820); True (17427) |
| season_league_competition_id | object | 0 | 0.00% | 356 |  |  |  |  | EFD1 (1918); IT2 (1858); IT1 (1676); ES1 (1618); ES2 (1596) |
| season_league_league_name | object | 0 | 0.00% | 569 |  |  |  |  | First Division (- 91/92) (1918); Serie B (1858); Serie A (1676); LaLiga (1618); Segunda División (1552) |
| season_league_league_slug | object | 0 | 0.00% | 352 |  |  |  |  | first-division-bis-91-92- (1918); serie-b (1858); bundesliga (1803); serie-a (1676); laliga (1618) |
| season_league_level_level_name | object | 0 | 0.00% | 10 |  |  |  |  | First Tier (27110); Second Tier (15816); Third Tier (7860); Fourth Tier (4352); Youth league (1610) |
| season_league_level_level_number | float64 | 2255 | 3.87% | 5 | 1.0000 | 5.0000 | 1.8574 | 1.0259 | 1.0 (27110); 2.0 (15816); 3.0 (7860); 4.0 (4352); NaN (2255) |
| season_league_season_id | int64 | 0 | 0.00% | 137 | 1888.0000 | 2025.0000 | 1997.3979 | 25.0344 | 2023 (1737); 2024 (1737); 2022 (1736); 2021 (1721); 2020 (1689) |
| season_losses | int64 | 0 | 0.00% | 37 | 0.0000 | 38.0000 | 10.9202 | 5.2313 | 11 (4253); 12 (4225); 10 (4036); 13 (4021); 9 (3889) |
| season_manager | float64 | 58247 | 100.00% | 0 |  |  |  |  | NaN (58247) |
| season_manager_manager_id | float64 | 10561 | 18.13% | 12671 | 2.0000 | 149038.0000 | 27918.0405 | 29523.7423 | NaN (10561); 5092.0 (52); 5106.0 (37); 5957.0 (35); 280.0 (34) |
| season_manager_manager_name | object | 10561 | 18.13% | 12656 |  |  |  |  | NaN (10561); Ricardo Ferretti (52); Víctor Manuel Vucetich (37); Miguel Herrera (35); Arsène Wenger (34) |
| season_manager_manager_slug | object | 10561 | 18.13% | 12653 |  |  |  |  | NaN (10561); ricardo-ferretti (52); victor-manuel-vucetich (37); miguel-herrera (35); arsene-wenger (34) |
| season_points | float64 | 17427 | 29.92% | 109 | 0.0000 | 111.0000 | 43.1763 | 18.1672 | NaN (17427); 42.0 (1002); 41.0 (970); 46.0 (969); 45.0 (965) |
| season_points_against | float64 | 40820 | 70.08% | 69 | 0.0000 | 71.0000 | 31.3113 | 10.7130 | NaN (40820); 34.0 (710); 36.0 (699); 33.0 (679); 37.0 (678) |
| season_points_for | float64 | 40820 | 70.08% | 70 | 0.0000 | 69.0000 | 33.4677 | 10.4723 | NaN (40820); 36.0 (773); 32.0 (741); 34.0 (735); 31.0 (713) |
| season_rank | int64 | 0 | 0.00% | 37 | 1.0000 | 37.0000 | 8.5290 | 5.4679 | 1 (4772); 2 (4350); 3 (4110); 4 (3972); 5 (3820) |
| season_season | object | 0 | 0.00% | 137 |  |  |  |  | 23/24 (1737); 24/25 (1737); 22/23 (1736); 21/22 (1721); 20/21 (1689) |
| season_total_matches | int64 | 0 | 0.00% | 50 | 0.0000 | 51.0000 | 31.2013 | 8.7672 | 34 (14474); 38 (9841); 30 (8723); 42 (3459); 26 (3380) |
| season_wins | int64 | 0 | 0.00% | 35 | 0.0000 | 34.0000 | 11.9147 | 5.4234 | 11 (4651); 10 (4573); 12 (4371); 9 (4161); 13 (4020) |
| team_name | object | 0 | 0.00% | 2161 |  |  |  |  | Arsenal FC (145); Everton FC (128); Aston Villa (125); Sunderland AFC (124); Newcastle United (119) |

#### Multi-column profiling

- Candidate primary keys: None detected
- Columns with >50% missing values: season_manager, season_points_against, season_points_for
- Possible join keys: team_id: [club_id]; competition_id: [competition_id]; season: [season_id]

| Column 1 | Column 2 | Correlation (|r|>=0.8) |
| --- | --- | --- |
| season_id | season_league_season_id | 1.0000 |
| season_points | season_wins | 0.9699 |
| season_losses | season_points_against | 0.9258 |
| season_points_for | season_wins | 0.9169 |
| season_goals_for | season_points | 0.8739 |
| season_goals_for | season_wins | 0.8485 |
| season_goals_against | season_losses | 0.8410 |

### Table: `datalake/transfermarkt/team_details/team_details.csv`

- Rows: 2175
- Columns: 12
- Duplicate rows: 0
- Duplicate row percentage: 0.00%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| club_id | int64 | 0 | 0.00% | 2175 | 1.0000 | 133273.0000 | 17617.8363 | 25064.3722 | 100335 (1); 46717 (1); 458 (1); 46823 (1); 472 (1) |
| club_slug | object | 0 | 0.00% | 2175 |  |  |  |  | cd-mafra-sub-23 (1); charlotte-independence (1); palermo-fc (1); toronto-fc-ii (1); ud-las-palmas (1) |
| club_name | object | 0 | 0.00% | 2175 |  |  |  |  | CD Mafra U23 (100335) (1); Charlotte Independence (46717) (1); Palermo FC (458) (1); Toronto FC II (46823) (1); UD Las Palmas (472) (1) |
| logo_url | object | 0 | 0.00% | 2166 |  |  |  |  | https://tmssl.akamaized.net//images/wappen/head/default.png?lm=1457423031 (10); https://tmssl.akamaized.net//images/wappen/head/100335.png?lm=1724075828 (1); https://tmssl.akamaized.net//images/wappen/head/46856.png?lm=1756638444 (1); https://tmssl.akamaized.net//images/wappen/head/4673.png?lm=1412763125 (1); https://tmssl.akamaized.net//images/wappen/head/468.png?lm=1485262132 (1) |
| country_name | object | 0 | 0.00% | 38 |  |  |  |  | Italy (345); France (212); England (122); Spain (119); United States (108) |
| season_id | int64 | 0 | 0.00% | 26 | 2000.0000 | 2025.0000 | 2013.7411 | 7.7394 | 2023 (143); 2024 (121); 2021 (113); 2022 (106); 2020 (103) |
| competition_id | object | 506 | 23.26% | 168 |  |  |  |  | NaN (506); ARG2 (36); MLS1 (30); ARGC (30); MNP3 (29) |
| competition_slug | object | 506 | 23.26% | 164 |  |  |  |  | NaN (506); primera-nacional (36); premier-liga (32); bundesliga (30); torneo-final (30) |
| competition_name | object | 506 | 23.26% | 164 |  |  |  |  | NaN (506); Primera Nacional (36); Premier Liga (32); Bundesliga (30); Major League Soccer (30) |
| club_division | object | 506 | 23.26% | 164 |  |  |  |  | NaN (506); Primera Nacional (36); Premier Liga (32); Bundesliga (30); Major League Soccer (30) |
| source_url | object | 0 | 0.00% | 2175 |  |  |  |  | https://www.transfermarkt.com/cd-mafra-sub-23/startseite/verein/100335/saison_id/2023 (1); https://www.transfermarkt.com/charlotte-independence/startseite/verein/46717/saison_id/2023 (1); https://www.transfermarkt.com/palermo-fc/startseite/verein/458/saison_id/2025 (1); https://www.transfermarkt.com/toronto-fc-ii/startseite/verein/46823/saison_id/2008 (1); https://www.transfermarkt.com/ud-las-palmas/startseite/verein/472/saison_id/2016 (1) |
| _last_modified_at | object | 0 | 0.00% | 1737 |  |  |  |  | 2025-09-13 09:17:08 (16); 2025-09-13 09:04:09 (13); 2025-09-13 09:31:36 (12); 2025-09-13 09:14:08 (11); 2025-09-13 09:37:04 (11) |

#### Multi-column profiling

- Candidate primary keys: club_id, club_slug, club_name, source_url
- Columns with >50% missing values: None
- Possible join keys: team_id: [club_id]; competition_id: [competition_id]; season: [season_id]

- High correlation pairs (|r|>=0.8): None

### Table: `datalake/transfermarkt/transfer_history/transfer_history.csv`

- Rows: 10000
- Columns: 10
- Duplicate rows: 2
- Duplicate row percentage: 0.02%

#### Column-level profiling

| Column | Data Type | Missing Values | Missing % | Unique Values | Min | Max | Mean | Std | Top 5 Frequent Values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| player_id | int64 | 0 | 0.00% | 1476 | 1.0000 | 1023412.0000 | 495688.5104 | 462674.1335 | 100011 (38); 101200 (38); 101347 (34); 101692 (33); 101254 (33) |
| season_name | object | 1 | 0.01% | 46 |  |  |  |  | 23/24 (1054); 24/25 (1005); 22/23 (937); 21/22 (619); 25/26 (522) |
| transfer_date | object | 8 | 0.08% | 2395 |  |  |  |  | 2022-07-01 (355); 2023-07-01 (324); 2024-07-01 (259); 2021-07-01 (226); 2025-07-01 (178) |
| from_team_id | int64 | 0 | 0.00% | 4735 | 1.0000 | 133816.0000 | 24101.3433 | 29023.8629 | 515 (323); 75 (103); 199 (30); 2113 (28); 15172 (28) |
| from_team_name | object | 0 | 0.00% | 4814 |  |  |  |  | Without Club (323); Unknown (103); Corinthians (30); Career break (28); Atlético-GO (28) |
| to_team_id | int64 | 0 | 0.00% | 4384 | 1.0000 | 134304.0000 | 20823.0568 | 27651.7529 | 515 (433); 123 (297); 75 (98); 199 (34); 2113 (30) |
| to_team_name | object | 0 | 0.00% | 4482 |  |  |  |  | Without Club (433); Retired (297); Unknown (98); Corinthians (34); Career break (30) |
| transfer_type | object | 0 | 0.00% | 4 |  |  |  |  | Transfer (7835); Loan (1083); Return from loan (1077); Draft (5) |
| value_at_transfer | int64 | 0 | 0.00% | 79 | 0.0000 | 50000000.0000 | 192877.0000 | 1195836.4438 | 0 (6596); 50000 (507); 100000 (382); 150000 (240); 200000 (231) |
| transfer_fee | int64 | 0 | 0.00% | 128 | 0.0000 | 57000000.0000 | 76375.2200 | 1079333.9182 | 0 (9740); 500000 (11); 300000 (10); 200000 (8); 400000 (7) |

#### Multi-column profiling

- Candidate primary keys: None detected
- Columns with >50% missing values: None
- Possible join keys: player_id: [player_id]; team_id: [from_team_id, to_team_id]; season: [season_name]

- High correlation pairs (|r|>=0.8): None

## Potential join keys

| Canonical Join Key | Detected Columns |
| --- | --- |
| competition_id | competition_id |
| player_id | player_id |
| player_name | name_in_home_country, player_name |
| season | season_id, season_name |
| team_id | club_id, current_club_id, from_team_id, team_id, to_team_id |

## Data quality observations

- Files with load errors: 0
- Large files sampled to 10,000 rows: 4
- Tables containing duplicate rows: player_injuries.csv (111), player_national_performances.csv (32), team_competitions_seasons.csv (360), transfer_history.csv (2)
- Tables containing columns with >50% missing values: player_national_performances.csv (1 columns), player_performances.csv (1 columns), player_profiles.csv (18 columns), player_teammates_played_with.csv (1 columns), team_competitions_seasons.csv (3 columns)
