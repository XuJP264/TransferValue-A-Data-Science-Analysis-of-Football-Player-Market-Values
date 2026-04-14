"""Main entry point for the v2 data preparation pipeline.

Usage:
    python TransferValue/v2/run_pipeline.py
    python TransferValue/v2/run_pipeline.py --stage 2   # run from stage 2 onward
"""

import sys
import time
import argparse

# Ensure v2 directory is on the path for imports
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline_config import get_logger, OUTPUTS_DIR

logger = get_logger("pipeline")


def main():
    parser = argparse.ArgumentParser(description="v2 Data Preparation Pipeline")
    parser.add_argument(
        "--stage", type=int, default=1, choices=[1, 2, 3, 4],
        help="Start from this stage (default: 1). Stages 2-4 will load from disk if needed."
    )
    args = parser.parse_args()

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    logger.info("=" * 60)
    logger.info("v2 Data Preparation Pipeline")
    logger.info("=" * 60)

    df = None  # Pass DataFrame between stages to avoid re-reading CSV

    # ── Stage 1: Profiling ───────────────────────────────────────────────
    if args.stage <= 1:
        from stage1_profiling import run_profiling
        run_profiling()

    # ── Stage 2: Structuring ─────────────────────────────────────────────
    if args.stage <= 2:
        from stage2_structuring import run_structuring
        df = run_structuring()

    # ── Stage 3: Cleaning ────────────────────────────────────────────────
    if args.stage <= 3:
        from stage3_cleaning import run_cleaning
        df = run_cleaning(df)

    # ── Stage 4: Enriching ───────────────────────────────────────────────
    if args.stage <= 4:
        from stage4_enriching import run_enriching
        df = run_enriching(df)

    elapsed = time.time() - t_start
    logger.info("=" * 60)
    logger.info(f"Pipeline complete in {elapsed:.1f}s")
    if df is not None:
        logger.info(f"Final dataset: {len(df):,} rows × {len(df.columns)} cols")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
