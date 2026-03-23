"""Stage 4: Enriching — Derived features based on cleaned data.

Feature engineering happens AFTER cleaning (fix issue #3).
"""

import pandas as pd
import numpy as np
import re

from pipeline_config import CLEANED_DIR, ENRICHED_DIR, get_logger, timed

logger = get_logger(__name__)


# ── 4.1 Performance efficiency features ─────────────────────────────────────

def _add_per90_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add per-90-minute efficiency metrics."""
    has_minutes = df["minutes_played"] > 0

    rate_features = {
        "goals_per_90": "goals",
        "assists_per_90": "assists",
        "goal_contributions_per_90": None,  # special: goals + assists
        "yellow_cards_per_90": "yellow_cards",
        "clean_sheets_per_90": "clean_sheets",
        "goals_conceded_per_90": "goals_conceded",
    }

    for feat, src in rate_features.items():
        if feat == "goal_contributions_per_90":
            df[feat] = 0.0
            df.loc[has_minutes, feat] = (
                (df.loc[has_minutes, "goals"] + df.loc[has_minutes, "assists"])
                / df.loc[has_minutes, "minutes_played"] * 90
            )
        elif src in df.columns:
            df[feat] = 0.0
            df.loc[has_minutes, feat] = (
                df.loc[has_minutes, src] / df.loc[has_minutes, "minutes_played"] * 90
            )

    return df


# ── 4.2 Age features ────────────────────────────────────────────────────────

def _add_age_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add age-derived features (fix issue #10: now age is properly filled)."""
    df["age_squared"] = df["age"] ** 2
    df["career_stage"] = pd.cut(
        df["age"],
        bins=[0, 21, 24, 28, 32, 50],
        labels=["youth", "emerging", "prime", "experienced", "veteran"],
        right=True,
    )
    return df


# ── 4.3 Market value change ─────────────────────────────────────────────────

def _add_market_value_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add market value change features (fix issue #6: no log transform)."""
    df["market_value_change"] = df["market_value"] - df["market_value_start"]

    has_start = df["market_value_start"] > 0
    df["market_value_change_pct"] = 0.0
    df.loc[has_start, "market_value_change_pct"] = (
        df.loc[has_start, "market_value_change"] / df.loc[has_start, "market_value_start"]
    )

    return df


# ── 4.4 Injury features ─────────────────────────────────────────────────────

def _add_injury_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add injury-derived features."""
    has_injuries = df["injury_count"] > 0
    df["injury_severity"] = 0.0
    df.loc[has_injuries, "injury_severity"] = (
        df.loc[has_injuries, "total_days_missed"] / df.loc[has_injuries, "injury_count"]
    )
    df["was_injured"] = (df["injury_count"] > 0).astype(int)
    return df


# ── 4.5 International experience ────────────────────────────────────────────

def _add_intl_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add international career features."""
    has_caps = df["intl_caps"] > 0
    df["intl_goals_per_cap"] = 0.0
    df.loc[has_caps, "intl_goals_per_cap"] = (
        df.loc[has_caps, "intl_goals"] / df.loc[has_caps, "intl_caps"]
    )
    df["has_intl_career"] = (df["intl_caps"] > 0).astype(int)
    return df


# ── 4.6 League encoding (fix issue #9) ──────────────────────────────────────

def _extract_tier(comp_id) -> int:
    """Extract league tier from competition_id (e.g. GB1→1, GB2→2, L1→1)."""
    if pd.isna(comp_id):
        return np.nan
    comp_str = str(comp_id)
    # Match trailing digits
    match = re.search(r"(\d+)$", comp_str)
    if match:
        return int(match.group(1))
    return np.nan


def _add_league_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add league tier and big-5 flags (fix issue #9: no ordinal encoding)."""
    if "competition_id" not in df.columns:
        # Use primary_competition_id if renamed
        comp_col = "primary_competition_id" if "primary_competition_id" in df.columns else None
    else:
        comp_col = "competition_id"

    if comp_col is None:
        logger.warning("No competition_id column found; skipping league features")
        return df

    df["league_tier"] = df[comp_col].apply(_extract_tier)
    df["is_top_division"] = (df["league_tier"] == 1).astype("Int64")

    # Big-5 league flags
    big5 = ["GB1", "ES1", "IT1", "L1", "FR1"]
    for league in big5:
        df[f"is_{league}"] = (df[comp_col] == league).astype(int)

    return df


# ── 4.8 Position encoding ───────────────────────────────────────────────────

def _add_position_encoding(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode main_position (Goalkeeper as baseline)."""
    if "main_position" not in df.columns:
        return df

    for pos in ["Defender", "Midfield", "Attack"]:
        df[f"pos_{pos}"] = (df["main_position"] == pos).astype(int)

    return df


# ── 4.10 Post-enrichment validation ─────────────────────────────────────────

def _validate(df: pd.DataFrame, cleaned_mv: pd.Series):
    """Run post-enrichment validation checks."""
    errors = []

    # 1. Check per-90 features for inf
    rate_cols = [c for c in df.columns if "per_90" in c or "per_cap" in c]
    inf_check = df[rate_cols].isin([np.inf, -np.inf])
    if inf_check.any().any():
        bad = inf_check.any()[inf_check.any()].index.tolist()
        errors.append(f"Inf values found in: {bad}")

    # 2. Check age_squared consistency
    if "age_squared" in df.columns:
        diff = (df["age_squared"] - df["age"] ** 2).abs()
        if (diff > 1e-6).any():
            errors.append("age_squared inconsistent with age**2")

    # 3. market_value not modified
    if not df["market_value"].equals(cleaned_mv):
        errors.append("market_value was modified during enrichment!")

    # 4. Excluded features should not exist
    for forbidden in ["log_market_value", "fee_to_value_ratio"]:
        if forbidden in df.columns:
            errors.append(f"Forbidden column exists: {forbidden}")

    if errors:
        for e in errors:
            logger.error(f"  VALIDATION FAIL: {e}")
        raise RuntimeError(f"Post-enrichment validation failed: {errors}")
    else:
        logger.info("  Post-enrichment validation PASSED ✓")


# ── Main ─────────────────────────────────────────────────────────────────────

@timed
def run_enriching(df: pd.DataFrame = None) -> pd.DataFrame:
    """Execute Stage 4: Enrich the cleaned dataset with derived features."""
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)

    if df is None:
        logger.info("Loading cleaned dataset from disk...")
        df = pd.read_csv(CLEANED_DIR / "cleaned_player_dataset.csv", low_memory=False)

    logger.info(f"Input: {len(df):,} rows, {len(df.columns)} cols")

    # Save market_value before enrichment for validation
    cleaned_mv = df["market_value"].copy()

    df = _add_per90_features(df)
    df = _add_age_features(df)
    df = _add_market_value_features(df)
    df = _add_injury_features(df)
    df = _add_intl_features(df)
    df = _add_league_features(df)
    df = _add_position_encoding(df)

    # Validate
    _validate(df, cleaned_mv)

    # ── Output 1: Full dataset with identifiers (for EDA) ────────────────
    full_path = ENRICHED_DIR / "enriched_player_dataset.csv"
    df.to_csv(full_path, index=False)
    logger.info(f"Written: {full_path} ({len(df):,} rows, {len(df.columns)} cols)")

    # ── Output 2: Modeling-ready (numeric/encoded only + target) ─────────
    id_cols = ["player_name", "season", "citizenship",
               "primary_team_name", "competition_name", "club_division",
               "ds_b_league", "is_eu", "position", "main_position", "foot",
               "career_stage"]
    drop_cols = [c for c in id_cols if c in df.columns]
    df_model = df.drop(columns=drop_cols, errors="ignore")

    # Drop any remaining object columns
    obj_cols = df_model.select_dtypes(include=["object"]).columns.tolist()
    if obj_cols:
        logger.info(f"  Dropping non-numeric columns from modeling set: {obj_cols}")
        df_model = df_model.drop(columns=obj_cols)

    model_path = ENRICHED_DIR / "enriched_modeling_ready.csv"
    df_model.to_csv(model_path, index=False)
    logger.info(f"Written: {model_path} ({len(df_model):,} rows, {len(df_model.columns)} cols)")

    # Report
    report_lines = [
        "# Stage 4: Enriching Report\n",
        f"- **Full dataset**: {len(df):,} rows × {len(df.columns)} cols",
        f"- **Modeling dataset**: {len(df_model):,} rows × {len(df_model.columns)} cols",
        "",
        "## New features added\n",
        "- Per-90 metrics: goals_per_90, assists_per_90, goal_contributions_per_90, etc.",
        "- Age: age_squared, career_stage",
        "- Market value: market_value_change, market_value_change_pct",
        "- Injury: injury_severity, was_injured",
        "- International: intl_goals_per_cap, has_intl_career",
        "- League: league_tier, is_top_division, is_GB1/ES1/IT1/L1/FR1",
        "- Position: pos_Defender, pos_Midfield, pos_Attack (one-hot)",
        "",
        "## Excluded features (by design)\n",
        "- log_market_value: NOT created (data leakage, fix issue #6)",
        "- fee_to_value_ratio: NOT created (97.67% missing, fix issue #8)",
    ]

    report_path = ENRICHED_DIR / "enriching_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))

    return df


if __name__ == "__main__":
    run_enriching()
