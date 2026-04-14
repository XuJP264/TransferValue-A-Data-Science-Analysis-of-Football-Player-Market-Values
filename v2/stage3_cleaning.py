"""Stage 3: Cleaning — Type fixes, deduplication, missing values, outliers.

Important: cleaning happens BEFORE feature engineering (fix issue #3).
"""

import pandas as pd
import numpy as np

from pipeline_config import STRUCTURED_DIR, CLEANED_DIR, get_logger, timed

logger = get_logger(__name__)


# ── 3.1 Type fixes ──────────────────────────────────────────────────────────

def _fix_types(df: pd.DataFrame) -> pd.DataFrame:
    """Fix column types (fix issue #13: player_id as nullable integer)."""
    df["player_id"] = df["player_id"].astype("Int64")
    return df


# ── 3.2 Deduplication ───────────────────────────────────────────────────────

def _deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicates and resolve (player_id, season) duplicates."""
    before = len(df)
    df = df.drop_duplicates()
    after_exact = len(df)
    if before != after_exact:
        logger.info(f"  Removed {before - after_exact} exact duplicates")

    # For (player_id, season) duplicates, keep the row with fewer NaNs
    dup_mask = df.duplicated(subset=["player_id", "season"], keep=False)
    if dup_mask.any():
        df["_nan_count"] = df.isna().sum(axis=1)
        df = df.sort_values("_nan_count")
        df = df.drop_duplicates(subset=["player_id", "season"], keep="first")
        df = df.drop(columns=["_nan_count"])
        logger.info(f"  Resolved (player_id, season) duplicates: {after_exact} → {len(df)}")

    return df


# ── 3.3 Missing value handling ──────────────────────────────────────────────

def _fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values with group-aware strategies."""

    # market_value: should already be filtered, drop any residual
    mv_missing = df["market_value"].isna().sum()
    if mv_missing > 0:
        logger.warning(f"  Dropping {mv_missing} residual rows with missing market_value")
        df = df.dropna(subset=["market_value"])

    # age: fill by (position, season) group median, then global median
    if "main_position" in df.columns:
        age_group_median = df.groupby(["main_position", "season"])["age"].transform("median")
        df["age"] = df["age"].fillna(age_group_median)
    age_global_median = df["age"].median()
    df["age"] = df["age"].fillna(age_global_median)
    logger.info(f"  age: remaining NaN = {df['age'].isna().sum()}")

    # goals, assists, minutes_played: fill by (main_position, competition_id, season) group median
    perf_cols = ["goals", "assists", "minutes_played"]
    group_cols_perf = []
    if "main_position" in df.columns:
        group_cols_perf.append("main_position")
    if "competition_id" in df.columns:
        group_cols_perf.append("competition_id")
    group_cols_perf.append("season")

    for col in perf_cols:
        if col in df.columns:
            if group_cols_perf:
                group_med = df.groupby(group_cols_perf)[col].transform("median")
                df[col] = df[col].fillna(group_med)
            df[col] = df[col].fillna(df[col].median())

    # height: fill by position group median
    if "height" in df.columns and "main_position" in df.columns:
        height_med = df.groupby("main_position")["height"].transform("median")
        df["height"] = df["height"].fillna(height_med)
        df["height"] = df["height"].fillna(df["height"].median())

    # Injury columns: NaN → 0 (no record = no injury)
    injury_cols = ["injury_count", "total_days_missed", "total_games_missed", "max_single_injury_days"]
    for col in injury_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # International columns: NaN → 0
    intl_cols = ["intl_caps", "intl_goals"]
    for col in intl_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Transfer columns: NaN → 0, had_loan → False
    transfer_num_cols = ["num_transfers", "total_transfer_fee", "max_transfer_fee"]
    for col in transfer_num_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    if "had_loan" in df.columns:
        df["had_loan"] = df["had_loan"].fillna(False)

    # club_division: keep NaN (真实缺失，不宜硬填)

    return df


# ── 3.3b Data consistency fixes ──────────────────────────────────────────────

def _fix_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """Fix contradictory records (e.g. minutes=0 but goals>0)."""
    perf_cols = ["goals", "assists", "own_goals", "penalty_goals",
                 "yellow_cards", "red_cards", "clean_sheets", "goals_conceded"]
    mask = df["minutes_played"] == 0
    for col in perf_cols:
        if col in df.columns:
            bad = mask & (df[col] > 0)
            if bad.any():
                logger.info(f"  {col}: zeroed {bad.sum()} rows where minutes_played=0")
                df.loc[mask, col] = 0
    return df


# ── 3.4 Outlier handling ────────────────────────────────────────────────────

def _handle_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Handle outliers with domain-knowledge and percentile-based clipping.

    IMPORTANT: market_value is NOT clipped (fix issue #5).
    """

    # Domain-knowledge caps
    domain_caps = {
        "goals": (0, 60),
        "assists": (0, 40),
        "minutes_played": (0, 5500),
    }
    for col, (lo, hi) in domain_caps.items():
        if col in df.columns:
            before_clip = df[col].describe()
            df[col] = df[col].clip(lower=lo, upper=hi)
            clipped = (df[col] != df[col]).sum()  # won't catch anything since clip is in-place
            logger.info(f"  {col}: clipped to [{lo}, {hi}] (was max={before_clip['max']:.0f})")

    # Percentile-based clipping (1st-99th)
    pct_cols = ["yellow_cards", "red_cards", "total_days_missed", "total_games_missed"]
    for col in pct_cols:
        if col in df.columns:
            p01 = df[col].quantile(0.01)
            p99 = df[col].quantile(0.99)
            df[col] = df[col].clip(lower=p01, upper=p99)
            logger.info(f"  {col}: clipped to [{p01:.1f}, {p99:.1f}] (1st-99th percentile)")

    return df


# ── 3.5 Category standardization ────────────────────────────────────────────

def _standardize_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize categorical variables."""

    # position / main_position → four categories
    position_map = {
        "goalkeeper": "Goalkeeper",
        "defender": "Defender",
        "midfield": "Midfield",
        "attack": "Attack",
    }

    # main_position → four broad categories (used for encoding/grouping)
    if "main_position" in df.columns:
        df["main_position"] = (
            df["main_position"]
            .astype(str)
            .str.split(" ").str[0]
            .str.strip()
            .str.lower()
            .map(position_map)
        )
        unmapped = df["main_position"].isna().sum()
        if unmapped > 0:
            logger.info(f"  main_position: {unmapped} values could not be mapped (set to NaN)")

    # position: keep original detail (e.g. "Attack - Right Winger") but clean "nan" strings
    if "position" in df.columns:
        df.loc[df["position"].astype(str).str.lower() == "nan", "position"] = np.nan

    # player_name: strip whitespace and remove trailing " (player_id)" suffix
    # e.g. "Lionel Messi (28003)" → "Lionel Messi"
    if "player_name" in df.columns:
        df["player_name"] = (
            df["player_name"]
            .astype(str)
            .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
            .str.strip()
        )
        # Convert "nan" string back to actual NaN
        df.loc[df["player_name"] == "nan", "player_name"] = np.nan

    return df


# ── Main ─────────────────────────────────────────────────────────────────────

@timed
def run_cleaning(df: pd.DataFrame = None) -> pd.DataFrame:
    """Execute Stage 3: Clean the structured dataset."""
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)

    if df is None:
        logger.info("Loading structured dataset from disk...")
        df = pd.read_csv(STRUCTURED_DIR / "structured_player_dataset.csv", low_memory=False)

    logger.info(f"Input: {len(df):,} rows, {len(df.columns)} cols")

    df = _fix_types(df)
    df = _deduplicate(df)
    df = _fill_missing(df)
    df = _fix_consistency(df)
    df = _handle_outliers(df)
    df = _standardize_categories(df)

    # Write output
    out_path = CLEANED_DIR / "cleaned_player_dataset.csv"
    df.to_csv(out_path, index=False)
    logger.info(f"Written: {out_path} ({len(df):,} rows, {len(df.columns)} cols)")

    # Report
    report_lines = [
        "# Stage 3: Cleaning Report\n",
        f"- **Output rows**: {len(df):,}",
        f"- **Output columns**: {len(df.columns)}",
        "",
        "## Missing values after cleaning\n",
    ]
    for col in df.columns:
        n_miss = df[col].isna().sum()
        if n_miss > 0:
            report_lines.append(f"- `{col}`: {n_miss} ({n_miss/len(df):.1%})")

    report_lines.extend([
        "",
        "## Key stats\n",
        f"- market_value: min={df['market_value'].min():,.0f}, max={df['market_value'].max():,.0f} (NOT clipped)",
        f"- goals: max={df['goals'].max():.0f} (cap=60)",
        f"- assists: max={df['assists'].max():.0f} (cap=40)",
        f"- minutes_played: max={df['minutes_played'].max():.0f} (cap=5500)",
        f"- age: min={df['age'].min():.1f}, max={df['age'].max():.1f}",
    ])

    report_path = CLEANED_DIR / "cleaning_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))

    return df


if __name__ == "__main__":
    run_cleaning()
