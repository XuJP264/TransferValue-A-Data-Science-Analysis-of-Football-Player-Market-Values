# Stage 4: Enriching Report

- **Full dataset**: 353,422 rows × 63 cols
- **Modeling dataset**: 353,422 rows × 50 cols

## New features added

- Per-90 metrics: goals_per_90, assists_per_90, goal_contributions_per_90, etc.
- Age: age_squared, career_stage
- Market value: market_value_change, market_value_change_pct
- Injury: injury_severity, was_injured
- International: intl_goals_per_cap, has_intl_career
- League: league_tier, is_top_division, is_GB1/ES1/IT1/L1/FR1
- Position: pos_Defender, pos_Midfield, pos_Attack (one-hot)

## Excluded features (by design)

- log_market_value: NOT created (data leakage, fix issue #6)
- fee_to_value_ratio: NOT created (97.67% missing, fix issue #8)