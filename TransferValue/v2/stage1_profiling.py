"""Stage 1: Data Profiling & Validation.

Validates data availability, generates profiling reports. No transformations.
"""

import json
import pandas as pd
import numpy as np

from pipeline_config import (
    ALL_SOURCE_FILES, PROFILING_DIR, get_logger, timed,
)

logger = get_logger(__name__)


def _is_lfs_pointer(path) -> bool:
    """Check if a file is a Git LFS pointer (first line starts with 'version https://git-lfs')."""
    try:
        with open(path, "r") as f:
            first_line = f.readline()
        return first_line.startswith("version https://git-lfs")
    except Exception:
        return False


def _profile_csv(path) -> dict:
    """Generate a profiling summary for a single CSV file."""
    info = {"file": path.name, "path": str(path)}

    if not path.exists():
        info["status"] = "MISSING"
        return info

    if _is_lfs_pointer(path):
        info["status"] = "LFS_POINTER"
        return info

    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception as e:
        info["status"] = f"READ_ERROR: {e}"
        return info

    info["status"] = "OK"
    info["rows"] = len(df)
    info["columns"] = len(df.columns)
    info["column_names"] = list(df.columns)
    info["dtypes"] = {col: str(df[col].dtype) for col in df.columns}
    info["missing_rate"] = {
        col: round(df[col].isna().mean(), 4) for col in df.columns
    }
    info["nunique"] = {col: int(df[col].nunique()) for col in df.columns}

    # Numeric stats
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    info["numeric_stats"] = {}
    for col in num_cols:
        info["numeric_stats"][col] = {
            "min": float(df[col].min()) if not df[col].isna().all() else None,
            "max": float(df[col].max()) if not df[col].isna().all() else None,
            "mean": float(df[col].mean()) if not df[col].isna().all() else None,
        }

    # player_id type check
    if "player_id" in df.columns:
        info["player_id_dtype"] = str(df["player_id"].dtype)

    return info


def _generate_report_md(profiles: list[dict]) -> str:
    """Generate a Markdown profiling report."""
    lines = ["# Data Profiling Report (v2 Pipeline)\n"]

    # player_id consistency check
    pid_types = {}
    for p in profiles:
        if "player_id_dtype" in p:
            pid_types[p["file"]] = p["player_id_dtype"]

    if pid_types:
        lines.append("## player_id Type Consistency\n")
        unique_types = set(pid_types.values())
        if len(unique_types) == 1:
            lines.append(f"All tables have `player_id` as `{unique_types.pop()}` ✓\n")
        else:
            lines.append("**WARNING**: Inconsistent player_id types:\n")
            for f, t in pid_types.items():
                lines.append(f"- `{f}`: `{t}`")
            lines.append("")

    # Per-file summaries
    lines.append("## File Summaries\n")
    for p in profiles:
        lines.append(f"### {p['file']}\n")
        lines.append(f"- **Status**: {p['status']}")
        if p["status"] != "OK":
            lines.append("")
            continue
        lines.append(f"- **Rows**: {p['rows']:,}")
        lines.append(f"- **Columns**: {p['columns']}")
        lines.append(f"- **Columns**: {', '.join(p['column_names'])}")

        # Top missing columns
        missing = {k: v for k, v in p["missing_rate"].items() if v > 0}
        if missing:
            sorted_missing = sorted(missing.items(), key=lambda x: -x[1])[:10]
            lines.append("- **Top missing columns**:")
            for col, rate in sorted_missing:
                lines.append(f"  - `{col}`: {rate:.1%}")

        if "player_id_dtype" in p:
            lines.append(f"- **player_id dtype**: `{p['player_id_dtype']}`")
        lines.append("")

    return "\n".join(lines)


@timed
def run_profiling() -> dict:
    """Execute Stage 1: Profile all source CSV files."""
    PROFILING_DIR.mkdir(parents=True, exist_ok=True)

    profiles = []
    for path in ALL_SOURCE_FILES:
        logger.info(f"Profiling {path.name}...")
        profile = _profile_csv(path)
        profiles.append(profile)
        if profile["status"] != "OK":
            logger.warning(f"  {path.name}: {profile['status']}")
        else:
            logger.info(f"  {path.name}: {profile['rows']:,} rows, {profile['columns']} cols")

    # Write outputs
    summary_path = PROFILING_DIR / "profiling_summary.json"
    with open(summary_path, "w") as f:
        json.dump(profiles, f, indent=2, default=str)
    logger.info(f"Written: {summary_path}")

    report_md = _generate_report_md(profiles)
    report_path = PROFILING_DIR / "profiling_report.md"
    with open(report_path, "w") as f:
        f.write(report_md)
    logger.info(f"Written: {report_path}")

    # Validate all OK
    bad = [p for p in profiles if p["status"] != "OK"]
    if bad:
        raise RuntimeError(
            f"Profiling failed for: {[p['file'] for p in bad]}. "
            "Fix data issues before proceeding."
        )

    return {"profiles": profiles}


if __name__ == "__main__":
    run_profiling()
