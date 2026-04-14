"""Shared configuration, paths, and utility functions for the v2 pipeline."""

from pathlib import Path
import logging
import time
from functools import wraps

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Dataset A: football-datasets (flat structure after re-download)
DS_A = PROJECT_ROOT / "football-datasets"
PLAYER_PERFORMANCES_CSV = DS_A / "player_performances" / "player_performances.csv"
PLAYER_PROFILES_CSV = DS_A / "player_profiles" / "player_profiles.csv"
PLAYER_MARKET_VALUE_CSV = DS_A / "player_market_value" / "player_market_value.csv"
PLAYER_INJURIES_CSV = DS_A / "player_injuries" / "player_injuries.csv"
PLAYER_NATIONAL_CSV = DS_A / "player_national_performances" / "player_national_performances.csv"
TEAM_COMPETITIONS_CSV = DS_A / "team_competitions_seasons" / "team_competitions_seasons.csv"
TRANSFER_HISTORY_CSV = DS_A / "transfer_history" / "transfer_history.csv"

# Dataset B
DS_B_TRANSFERS_CSV = PROJECT_ROOT / "football-transfers-data" / "dataset" / "transfers.csv"

# All source files for validation
ALL_SOURCE_FILES = [
    PLAYER_PERFORMANCES_CSV,
    PLAYER_PROFILES_CSV,
    PLAYER_MARKET_VALUE_CSV,
    PLAYER_INJURIES_CSV,
    PLAYER_NATIONAL_CSV,
    TEAM_COMPETITIONS_CSV,
    TRANSFER_HISTORY_CSV,
    DS_B_TRANSFERS_CSV,
]

# Output paths
V2_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = V2_DIR / "outputs"
PROFILING_DIR = OUTPUTS_DIR / "profiling"
STRUCTURED_DIR = OUTPUTS_DIR / "structured"
CLEANED_DIR = OUTPUTS_DIR / "cleaned"
ENRICHED_DIR = OUTPUTS_DIR / "enriched"

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def get_logger(name: str) -> logging.Logger:
    """Return a logger with consistent formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# ── Season helpers ───────────────────────────────────────────────────────────

def season_to_midpoint_date(season: str):
    """Convert season string like '08/09' to midpoint date (Jan 15 of end year).

    Returns pd.Timestamp or pd.NaT if unparseable.
    """
    import pandas as pd
    try:
        parts = season.split("/")
        if len(parts) == 2:
            yy_end = int(parts[1])
            year_end = 2000 + yy_end if yy_end < 100 else yy_end
            return pd.Timestamp(year=year_end, month=1, day=15)
    except (ValueError, IndexError):
        pass
    return pd.NaT


def season_start_date(season: str):
    """Return Aug 1 of the starting year for a season like '08/09'."""
    import pandas as pd
    try:
        parts = season.split("/")
        yy_start = int(parts[0])
        year_start = 2000 + yy_start if yy_start < 100 else yy_start
        return pd.Timestamp(year=year_start, month=8, day=1)
    except (ValueError, IndexError):
        return pd.NaT


def season_end_date(season: str):
    """Return Jun 30 of the ending year for a season like '08/09'."""
    import pandas as pd
    try:
        parts = season.split("/")
        yy_end = int(parts[1])
        year_end = 2000 + yy_end if yy_end < 100 else yy_end
        return pd.Timestamp(year=year_end, month=6, day=30)
    except (ValueError, IndexError):
        return pd.NaT


def date_to_season(date_str: str) -> str:
    """Convert ISO date (e.g. '2023-12-19') to season string like '23/24'.

    Rule: month >= 8 → season starts this year; month <= 7 → season started last year.
    """
    import pandas as pd
    try:
        dt = pd.Timestamp(date_str)
        if dt.month >= 8:
            start_year = dt.year
        else:
            start_year = dt.year - 1
        end_year = start_year + 1
        return f"{start_year % 100:02d}/{end_year % 100:02d}"
    except Exception:
        return ""


def int_season_to_str(season_int: int) -> str:
    """Convert integer season (e.g. 2009) to string '08/09'."""
    start = season_int - 1
    return f"{start % 100:02d}/{season_int % 100:02d}"


# ── Timing decorator ────────────────────────────────────────────────────────

def timed(func):
    """Decorator that logs execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(f"Starting {func.__name__}...")
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        logger.info(f"Finished {func.__name__} in {elapsed:.1f}s")
        return result
    return wrapper
