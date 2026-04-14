"""Stage 2: Structuring — Multi-table join into player-season granularity.

Spine table: player_performances aggregated to (player_id, season_name).
LEFT JOINs: profiles → market_value → injuries → national → team_context → transfer_history → dataset_b.
"""

import pandas as pd
import numpy as np

from pipeline_config import (
    PLAYER_PERFORMANCES_CSV, PLAYER_PROFILES_CSV, PLAYER_MARKET_VALUE_CSV,
    PLAYER_INJURIES_CSV, PLAYER_NATIONAL_CSV, TEAM_COMPETITIONS_CSV,
    TRANSFER_HISTORY_CSV, DS_B_TRANSFERS_CSV, STRUCTURED_DIR,
    date_to_season, season_end_date, season_start_date,
    season_to_midpoint_date, int_season_to_str,
    get_logger, timed,
)

logger = get_logger(__name__)


# ── 2.1 Player Performances → player-season ─────────────────────────────────

def _load_performances() -> pd.DataFrame:
    """Load and aggregate player_performances to (player_id, season_name)."""
    logger.info("Loading player_performances...")
    df = pd.read_csv(PLAYER_PERFORMANCES_CSV, low_memory=False)
    logger.info(f"  Raw rows: {len(df):,}")

    # Parse minutes_played: remove ' and . (thousands separator), e.g. "1.580'" → 1580
    df["minutes_played"] = (
        df["minutes_played"]
        .astype(str)
        .str.replace("'", "", regex=False)
        .str.replace(".", "", regex=False)
    )
    df["minutes_played"] = pd.to_numeric(df["minutes_played"], errors="coerce")

    # Ensure numeric columns
    num_cols = ["goals", "assists", "own_goals", "yellow_cards",
                "second_yellow_cards", "direct_red_cards", "penalty_goals",
                "minutes_played", "goals_conceded", "clean_sheets"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Determine primary_team per (player_id, season_name): team with most minutes
    team_minutes = (
        df.groupby(["player_id", "season_name", "team_id", "team_name"])["minutes_played"]
        .sum()
        .reset_index()
    )
    idx_max = team_minutes.groupby(["player_id", "season_name"])["minutes_played"].idxmax()
    primary_teams = team_minutes.loc[idx_max, ["player_id", "season_name", "team_id", "team_name"]].copy()
    primary_teams.rename(columns={"team_id": "primary_team_id", "team_name": "primary_team_name"}, inplace=True)

    # Count distinct teams per player-season
    num_teams = (
        df.groupby(["player_id", "season_name"])["team_id"]
        .nunique()
        .reset_index()
        .rename(columns={"team_id": "num_teams"})
    )

    # Aggregate stats
    agg_dict = {
        "goals": "sum",
        "assists": "sum",
        "own_goals": "sum",
        "minutes_played": "sum",
        "yellow_cards": "sum",
        "second_yellow_cards": "sum",
        "direct_red_cards": "sum",
        "penalty_goals": "sum",
        "goals_conceded": "sum",
        "clean_sheets": "sum",
    }
    # nb_in_group represents appearances per competition entry
    if "nb_in_group" in df.columns:
        agg_dict["nb_in_group"] = "sum"

    agg = df.groupby(["player_id", "season_name"]).agg(agg_dict).reset_index()

    # Rename nb_in_group → appearances
    if "nb_in_group" in agg.columns:
        agg.rename(columns={"nb_in_group": "appearances"}, inplace=True)

    # Combine red cards
    agg["red_cards"] = agg["second_yellow_cards"].fillna(0) + agg["direct_red_cards"].fillna(0)
    agg.drop(columns=["second_yellow_cards", "direct_red_cards"], inplace=True)

    # Merge primary team and num_teams
    agg = agg.merge(primary_teams, on=["player_id", "season_name"], how="left")
    agg = agg.merge(num_teams, on=["player_id", "season_name"], how="left")

    logger.info(f"  Aggregated to {len(agg):,} player-seasons")
    return agg


# ── 2.2 Player Profiles ─────────────────────────────────────────────────────

def _load_profiles() -> pd.DataFrame:
    """Load player_profiles, keep relevant columns."""
    logger.info("Loading player_profiles...")
    df = pd.read_csv(PLAYER_PROFILES_CSV, low_memory=False)
    keep = ["player_id", "player_name", "date_of_birth", "height",
            "citizenship", "is_eu", "position", "main_position", "foot"]
    df = df[[c for c in keep if c in df.columns]].copy()

    # height == 0.0 → NaN
    if "height" in df.columns:
        df.loc[df["height"] == 0.0, "height"] = np.nan

    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")

    logger.info(f"  Loaded {len(df):,} profiles")
    return df


# ── 2.3 Player Market Value ─────────────────────────────────────────────────

def _load_market_value() -> pd.DataFrame:
    """Load player_market_value and pick season-end + season-start values.

    date_unix is actually ISO date. Convert to season, then:
    - market_value: observation closest to season end (Jun 30)
    - market_value_start: observation closest to season start (Aug 1)
    """
    logger.info("Loading player_market_value...")
    df = pd.read_csv(PLAYER_MARKET_VALUE_CSV, low_memory=False)
    logger.info(f"  Raw rows: {len(df):,}")

    df["date"] = pd.to_datetime(df["date_unix"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"])

    # Assign season
    df["season_name"] = df["date_unix"].apply(date_to_season)
    df = df[df["season_name"] != ""].copy()

    # Season end date for each row
    df["season_end"] = df["season_name"].apply(season_end_date)
    df["season_start"] = df["season_name"].apply(season_start_date)
    df["dist_to_end"] = (df["date"] - df["season_end"]).abs()
    df["dist_to_start"] = (df["date"] - df["season_start"]).abs()

    # Market value at season end: closest observation to Jun 30
    idx_end = df.groupby(["player_id", "season_name"])["dist_to_end"].idxmin()
    mv_end = df.loc[idx_end, ["player_id", "season_name", "value"]].rename(
        columns={"value": "market_value"}
    )

    # Market value at season start: closest observation to Aug 1
    idx_start = df.groupby(["player_id", "season_name"])["dist_to_start"].idxmin()
    mv_start = df.loc[idx_start, ["player_id", "season_name", "value"]].rename(
        columns={"value": "market_value_start"}
    )

    result = mv_end.merge(mv_start, on=["player_id", "season_name"], how="outer")
    logger.info(f"  Market value records: {len(result):,} player-seasons")
    return result


# ── 2.4 Player Injuries ─────────────────────────────────────────────────────

def _load_injuries() -> pd.DataFrame:
    """Aggregate injuries to (player_id, season_name)."""
    logger.info("Loading player_injuries...")
    df = pd.read_csv(PLAYER_INJURIES_CSV, low_memory=False)
    logger.info(f"  Raw rows: {len(df):,}")

    df["days_missed"] = pd.to_numeric(df["days_missed"], errors="coerce")
    df["games_missed"] = pd.to_numeric(df["games_missed"], errors="coerce")

    agg = df.groupby(["player_id", "season_name"]).agg(
        injury_count=("injury_reason", "count"),
        total_days_missed=("days_missed", "sum"),
        total_games_missed=("games_missed", "sum"),
        max_single_injury_days=("days_missed", "max"),
    ).reset_index()

    logger.info(f"  Injury records: {len(agg):,} player-seasons")
    return agg


# ── 2.5 National Performances ───────────────────────────────────────────────

def _load_national() -> pd.DataFrame:
    """Aggregate national performances to player level (not season)."""
    logger.info("Loading player_national_performances...")
    df = pd.read_csv(PLAYER_NATIONAL_CSV, low_memory=False)
    logger.info(f"  Raw rows: {len(df):,}")

    df["matches"] = pd.to_numeric(df["matches"], errors="coerce")
    df["goals"] = pd.to_numeric(df["goals"], errors="coerce")

    agg = df.groupby("player_id").agg(
        intl_caps=("matches", "sum"),
        intl_goals=("goals", "sum"),
    ).reset_index()

    logger.info(f"  National records: {len(agg):,} players")
    return agg


# ── 2.6 Team Competitions Seasons ───────────────────────────────────────────

def _load_team_competitions() -> pd.DataFrame:
    """Load team_competitions_seasons (7-column version, no match results)."""
    logger.info("Loading team_competitions_seasons...")
    df = pd.read_csv(TEAM_COMPETITIONS_CSV, low_memory=False)
    logger.info(f"  Raw rows: {len(df):,}")

    # season_id is integer (e.g. 2023), convert to season string for join
    df["season_id"] = pd.to_numeric(df["season_id"], errors="coerce")
    df["season_name"] = df["season_id"].apply(
        lambda x: int_season_to_str(int(x)) if pd.notna(x) else ""
    )

    # Keep relevant columns, rename for join
    df = df[["club_id", "season_name", "competition_id", "competition_name", "club_division"]].copy()
    df.rename(columns={"club_id": "primary_team_id"}, inplace=True)

    # Deduplicate: a team can have multiple competitions per season; keep first
    df = df.drop_duplicates(subset=["primary_team_id", "season_name"], keep="first")

    logger.info(f"  Team-season records: {len(df):,}")
    return df


# ── 2.7 Transfer History ────────────────────────────────────────────────────

def _load_transfer_history() -> pd.DataFrame:
    """Aggregate transfer_history to (player_id, season_name)."""
    logger.info("Loading transfer_history...")
    df = pd.read_csv(TRANSFER_HISTORY_CSV, low_memory=False)
    logger.info(f"  Raw rows: {len(df):,}")

    df["transfer_fee"] = pd.to_numeric(df["transfer_fee"], errors="coerce")
    df["value_at_transfer"] = pd.to_numeric(df["value_at_transfer"], errors="coerce")

    # Detect loans
    df["is_loan"] = df["transfer_type"].str.contains("loan", case=False, na=False).astype(int)

    agg = df.groupby(["player_id", "season_name"]).agg(
        num_transfers=("transfer_date", "count"),
        total_transfer_fee=("transfer_fee", "sum"),
        max_transfer_fee=("transfer_fee", "max"),
        had_loan=("is_loan", "max"),
    ).reset_index()

    agg["had_loan"] = agg["had_loan"].astype(bool)

    logger.info(f"  Transfer history records: {len(agg):,} player-seasons")
    return agg


# ── 2.8 Dataset B Transfers ─────────────────────────────────────────────────

def _load_dataset_b() -> pd.DataFrame:
    """Load Dataset B transfers.csv for supplementary age and league info."""
    logger.info("Loading Dataset B transfers...")
    df = pd.read_csv(DS_B_TRANSFERS_CSV, low_memory=False)
    logger.info(f"  Raw rows: {len(df):,}")

    # Convert integer season to string: 2009 → '08/09'
    df["season_name"] = df["season"].apply(
        lambda x: int_season_to_str(int(x)) if pd.notna(x) else ""
    )

    # Keep one record per (player_id, season_name): take first occurrence
    df = df.sort_values("player_id")
    dedup = df.drop_duplicates(subset=["player_id", "season_name"], keep="first")

    result = dedup[["player_id", "season_name", "player_age", "league"]].copy()
    result.rename(columns={"league": "ds_b_league"}, inplace=True)

    logger.info(f"  Dataset B records: {len(result):,} player-seasons")
    return result


# ── 2.9 Master Join ─────────────────────────────────────────────────────────

@timed
def run_structuring() -> pd.DataFrame:
    """Execute Stage 2: Build the master player-season dataset."""
    STRUCTURED_DIR.mkdir(parents=True, exist_ok=True)

    # Load all sources
    spine = _load_performances()
    profiles = _load_profiles()
    market_value = _load_market_value()
    injuries = _load_injuries()
    national = _load_national()
    team_ctx = _load_team_competitions()
    transfers = _load_transfer_history()
    ds_b = _load_dataset_b()

    logger.info("Performing master join...")

    # LEFT JOIN profiles (player-level, no season)
    df = spine.merge(profiles, on="player_id", how="left")

    # LEFT JOIN market_value
    df = df.merge(market_value, on=["player_id", "season_name"], how="left")

    # LEFT JOIN injuries
    df = df.merge(injuries, on=["player_id", "season_name"], how="left")

    # LEFT JOIN national (player-level)
    df = df.merge(national, on="player_id", how="left")

    # LEFT JOIN team context on (primary_team_id, season_name)
    df["primary_team_id"] = pd.to_numeric(df["primary_team_id"], errors="coerce")
    team_ctx["primary_team_id"] = pd.to_numeric(team_ctx["primary_team_id"], errors="coerce")
    df = df.merge(team_ctx, on=["primary_team_id", "season_name"], how="left")

    # LEFT JOIN transfer history
    df = df.merge(transfers, on=["player_id", "season_name"], how="left")

    # LEFT JOIN Dataset B
    df = df.merge(ds_b, on=["player_id", "season_name"], how="left")

    # ── Compute age (fix issue #1) ───────────────────────────────────────
    df["season_midpoint"] = df["season_name"].apply(season_to_midpoint_date)
    df["age"] = (df["season_midpoint"] - df["date_of_birth"]).dt.days / 365.25
    # Backfill with Dataset B player_age where our computed age is missing
    df["age"] = df["age"].fillna(df["player_age"])
    # Drop helper columns
    df.drop(columns=["season_midpoint", "date_of_birth", "player_age"], inplace=True)

    # Rename season_name → season for cleaner output
    df.rename(columns={"season_name": "season"}, inplace=True)

    logger.info(f"Master dataset before filtering: {len(df):,} rows")

    # ── 2.10 Filter: drop rows without market_value or with 0 (fix issue #12) ──
    before = len(df)
    df = df.dropna(subset=["market_value"])
    after_na = len(df)
    df = df[df["market_value"] > 0]
    after = len(df)
    logger.info(
        f"Filtered market_value: {before:,} → {after:,} "
        f"(NaN: -{before - after_na:,}, zero: -{after_na - after:,})"
    )

    # ── Write output ─────────────────────────────────────────────────────
    out_path = STRUCTURED_DIR / "structured_player_dataset.csv"
    df.to_csv(out_path, index=False)
    logger.info(f"Written: {out_path} ({len(df):,} rows, {len(df.columns)} cols)")

    # Write a brief report
    report_lines = [
        "# Stage 2: Structuring Report\n",
        f"- **Output rows**: {len(df):,}",
        f"- **Output columns**: {len(df.columns)}",
        f"- **Columns**: {', '.join(df.columns)}",
        f"- **market_value missing**: {df['market_value'].isna().sum()} (should be 0)",
        f"- **age missing**: {df['age'].isna().sum()} ({df['age'].isna().mean():.1%})",
        f"- **Unique players**: {df['player_id'].nunique():,}",
        f"- **Season range**: {df['season'].min()} to {df['season'].max()}",
    ]
    report_path = STRUCTURED_DIR / "structuring_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))

    return df


if __name__ == "__main__":
    run_structuring()
