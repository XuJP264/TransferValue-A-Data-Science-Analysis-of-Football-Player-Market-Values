from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(r"D:\PythonProject\TransferValue")

DATASET_DIRS = {
    "Dataset A": PROJECT_ROOT / "football-datasets",
    "Dataset B": PROJECT_ROOT / "football-transfers-data",
    "Dataset C": PROJECT_ROOT / "Modelling-Football-Players-Values-on-a-Transfer-Market",
}

SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".json", ".xlsx"}
IGNORED_DIR_NAMES = {"images", "scrapers", "code", "__pycache__", ".git"}
MAX_ROWS = 10_000
PREVIEW_ROWS = 5


def log_info(msg: str) -> None:
    print(f"[INFO] {msg}")


def log_warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def log_error(msg: str) -> None:
    print(f"[ERROR] {msg}")


def file_size_mb(path: Path) -> float:
    return round(path.stat().st_size / (1024 * 1024), 3)


def normalize_column_name(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum() or ch == "_")


def should_skip_path(path: Path, root: Path) -> bool:
    try:
        relative_parts = [p.lower() for p in path.relative_to(root).parts]
    except ValueError:
        relative_parts = [p.lower() for p in path.parts]
    return any(part in IGNORED_DIR_NAMES for part in relative_parts)


def discover_data_files(dataset_root: Path) -> list[Path]:
    discovered: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(dataset_root):
        current_dir = Path(dirpath)
        dirnames[:] = [d for d in dirnames if d.lower() not in IGNORED_DIR_NAMES]
        for filename in filenames:
            file_path = current_dir / filename
            if should_skip_path(file_path, dataset_root):
                continue
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                discovered.append(file_path)
    return sorted(discovered)


def try_read_csv(path: Path, sep: str, nrows: int) -> pd.DataFrame:
    encodings = ["utf-8", "utf-8-sig", "latin1"]
    last_err: Exception | None = None
    for enc in encodings:
        try:
            return pd.read_csv(path, sep=sep, nrows=nrows, low_memory=False, encoding=enc)
        except Exception as err:  # pragma: no cover - defensive
            last_err = err
    if last_err:
        raise last_err
    raise RuntimeError(f"Failed to read {path}")


def try_read_json(path: Path, nrows: int) -> pd.DataFrame:
    # 1) Attempt JSON lines first.
    try:
        return pd.read_json(path, lines=True, nrows=nrows)
    except Exception:
        pass

    # 2) Attempt regular JSON.
    try:
        df = pd.read_json(path)
        return df.head(nrows)
    except Exception:
        pass

    # 3) Fallback through json module for nested structures.
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        obj = json.load(f)

    if isinstance(obj, list):
        return pd.json_normalize(obj[:nrows])

    if isinstance(obj, dict):
        list_candidates = [v for v in obj.values() if isinstance(v, list)]
        if list_candidates:
            return pd.json_normalize(list_candidates[0][:nrows])
        return pd.json_normalize(obj)

    return pd.DataFrame({"value": [obj]})


def load_file_sample(path: Path, max_rows: int = MAX_ROWS) -> tuple[pd.DataFrame, str]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return try_read_csv(path, sep=",", nrows=max_rows), ""
    if suffix == ".tsv":
        return try_read_csv(path, sep="\t", nrows=max_rows), ""
    if suffix == ".json":
        return try_read_json(path, nrows=max_rows), ""
    if suffix == ".xlsx":
        return pd.read_excel(path, nrows=max_rows), ""
    raise ValueError(f"Unsupported file extension: {path.suffix}")


def estimate_total_rows(path: Path, sampled_rows: int) -> int | None:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                line_count = sum(1 for _ in f)
            return max(line_count - 1, 0)
        except Exception:
            return sampled_rows
    return sampled_rows


def markdown_escape(value: Any) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int = PREVIEW_ROWS) -> str:
    if df.empty:
        return "_No rows available._"

    df_preview = df.head(max_rows).copy()
    cols = list(df_preview.columns)
    header = "| " + " | ".join(markdown_escape(c) for c in cols) + " |"
    divider = "| " + " | ".join("---" for _ in cols) + " |"
    rows: list[str] = []
    for _, row in df_preview.iterrows():
        rows.append("| " + " | ".join(markdown_escape(row[c]) for c in cols) + " |")
    return "\n".join([header, divider, *rows])


def schema_to_markdown(schema_rows: list[dict[str, Any]]) -> str:
    if not schema_rows:
        return "_No columns available._"
    lines = [
        "| Column | Data Type | Missing Values |",
        "|---|---|---|",
    ]
    for row in schema_rows:
        lines.append(
            f"| {markdown_escape(row['column'])} | "
            f"{markdown_escape(row['dtype'])} | "
            f"{markdown_escape(row['missing'])} |"
        )
    return "\n".join(lines)


def extract_file_metadata(path: Path, dataset_root: Path) -> dict[str, Any]:
    rel_path = path.relative_to(dataset_root)
    info: dict[str, Any] = {
        "file_name": path.name,
        "file_path": path,
        "relative_path": str(rel_path).replace("\\", "/"),
        "file_size_mb": file_size_mb(path),
        "rows": 0,
        "columns": 0,
        "column_names": [],
        "dtypes": {},
        "missing_counts": {},
        "preview_df": pd.DataFrame(),
        "schema_rows": [],
        "load_error": None,
        "sampled": False,
    }

    try:
        df_sample, _ = load_file_sample(path, max_rows=MAX_ROWS)
        if len(df_sample) >= MAX_ROWS:
            info["sampled"] = True
        total_rows = estimate_total_rows(path, len(df_sample))

        info["rows"] = int(total_rows) if total_rows is not None else int(len(df_sample))
        info["columns"] = int(df_sample.shape[1])
        info["column_names"] = [str(c) for c in df_sample.columns.tolist()]
        info["dtypes"] = {str(c): str(t) for c, t in df_sample.dtypes.items()}
        info["missing_counts"] = {str(c): int(v) for c, v in df_sample.isna().sum().items()}
        info["preview_df"] = df_sample.head(PREVIEW_ROWS).copy()
        info["schema_rows"] = [
            {
                "column": str(col),
                "dtype": str(dtype),
                "missing": int(info["missing_counts"].get(str(col), 0)),
            }
            for col, dtype in df_sample.dtypes.items()
        ]
    except Exception as err:  # pragma: no cover - defensive
        info["load_error"] = str(err)
        log_error(f"Failed loading {path}: {err}")

    return info


def canonical_column_map(columns: list[str]) -> dict[str, list[str]]:
    normalized = {col: normalize_column_name(col) for col in columns}

    patterns: dict[str, set[str]] = {
        "player_id": {"player_id", "playerid"},
        "player_name": {"player_name", "name_in_home_country", "fullname", "full_name", "player"},
        "team_id": {"team_id", "club_id", "current_club_id", "from_team_id", "to_team_id", "counter_team_id"},
        "team_name": {"team_name", "club_name", "current_club_name", "from_team_name", "to_team_name", "counter_team_name"},
        "season": {"season", "season_name", "season_id"},
        "age": {"age", "player_age"},
        "position": {"position", "player_pos", "main_position"},
        "league": {"league", "competition_name", "competition_id", "competition_slug"},
        "transfer_fee": {"transfer_fee", "transfer_fee_amnt"},
        "market_value": {"market_value", "market_val_amnt", "value", "value_at_transfer"},
    }

    mapped: dict[str, list[str]] = {}
    for canonical, pats in patterns.items():
        hits = []
        for original, norm in normalized.items():
            if norm in pats:
                hits.append(original)
        if hits:
            mapped[canonical] = hits
    return mapped


def build_dataset_structure_markdown(dataset_results: dict[str, dict[str, Any]]) -> str:
    lines: list[str] = ["# Dataset Structure Overview", ""]

    for dataset_label, payload in dataset_results.items():
        lines.append(f"## {dataset_label} — {payload['folder_name']}")
        lines.append("")
        lines.append("### Folder structure")
        lines.append("")
        if not payload["files"]:
            lines.append("_No supported data files detected._")
            lines.append("")
            continue
        for file_meta in payload["files"]:
            lines.append(
                f"- `{file_meta['relative_path']}` "
                f"({file_meta['file_size_mb']:.3f} MB)"
            )
        lines.append("")

        for file_meta in payload["files"]:
            lines.append(f"### File: {file_meta['file_name']}")
            lines.append("")
            if file_meta["load_error"]:
                lines.append(f"_Failed to load file: {markdown_escape(file_meta['load_error'])}_")
                lines.append("")
                continue

            sampled_note = " (profiled on first 10,000 rows)" if file_meta["sampled"] else ""
            lines.append(f"Rows: {file_meta['rows']}{sampled_note}  ")
            lines.append(f"Columns: {file_meta['columns']}")
            lines.append("")
            lines.append("Schema:")
            lines.append("")
            lines.append(schema_to_markdown(file_meta["schema_rows"]))
            lines.append("")
            lines.append("Preview:")
            lines.append("")
            lines.append(dataframe_to_markdown(file_meta["preview_df"], max_rows=PREVIEW_ROWS))
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def infer_dataset_purpose(dataset_label: str, folder_name: str, file_count: int) -> str:
    if dataset_label == "Dataset A":
        return (
            "Comprehensive Transfermarkt-style football datalake with player profiles, "
            "performances, market values, injuries, transfers, and team context."
        )
    if dataset_label == "Dataset B":
        return (
            "European transfer-market dataset centered on transfer transactions, "
            "transfer fees, market values at transfer, and league-season metadata."
        )
    if file_count == 0:
        return (
            "Modeling-focused repository with notebooks and scripts; no supported local "
            "tabular data files were detected under current discovery rules."
        )
    return (
        f"Repository `{folder_name}` includes additional structured data potentially used "
        "for player value modeling and feature engineering."
    )


def pick_relevant_files(file_metas: list[dict[str, Any]], max_files: int = 5) -> list[dict[str, Any]]:
    def score(meta: dict[str, Any]) -> int:
        fname = meta["file_name"].lower()
        keywords = ["profile", "market", "value", "transfer", "performance", "player", "team", "season"]
        key_score = sum(1 for k in keywords if k in fname)
        col_score = len(canonical_column_map(meta.get("column_names", [])))
        return key_score * 3 + col_score

    valid = [m for m in file_metas if not m.get("load_error")]
    return sorted(valid, key=score, reverse=True)[:max_files]


def build_join_candidates(dataset_results: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    selected_by_dataset: dict[str, list[dict[str, Any]]] = {}
    for dlabel, payload in dataset_results.items():
        selected_by_dataset[dlabel] = pick_relevant_files(payload["files"], max_files=5)

    dataset_labels = list(selected_by_dataset.keys())
    output_rows: list[dict[str, str]] = []
    allowed_join_keys = {"player_id", "player_name", "team_id", "team_name", "season", "age", "position", "league"}

    for i in range(len(dataset_labels)):
        for j in range(i + 1, len(dataset_labels)):
            d1, d2 = dataset_labels[i], dataset_labels[j]
            for f1 in selected_by_dataset[d1]:
                c1 = canonical_column_map(f1.get("column_names", []))
                for f2 in selected_by_dataset[d2]:
                    c2 = canonical_column_map(f2.get("column_names", []))
                    common = sorted((set(c1.keys()) & set(c2.keys())) & allowed_join_keys)
                    for ck in common:
                        output_rows.append(
                            {
                                "dataset_left": d1,
                                "file_left": f1["relative_path"],
                                "dataset_right": d2,
                                "file_right": f2["relative_path"],
                                "join_key": ck,
                                "left_column": c1[ck][0],
                                "right_column": c2[ck][0],
                            }
                        )

    dedup: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for row in output_rows:
        key = (
            row["dataset_left"],
            row["file_left"],
            row["dataset_right"],
            row["file_right"],
            row["join_key"],
        )
        if key not in dedup:
            dedup[key] = row
    return list(dedup.values())


def build_dataset_relationship_markdown(dataset_results: dict[str, dict[str, Any]]) -> str:
    lines: list[str] = ["# Dataset Relationship Analysis", ""]

    for dataset_label, payload in dataset_results.items():
        lines.append(f"## {dataset_label}")
        lines.append(
            infer_dataset_purpose(
                dataset_label=dataset_label,
                folder_name=payload["folder_name"],
                file_count=len(payload["files"]),
            )
        )
        lines.append("")
        if payload["files"]:
            representative = pick_relevant_files(payload["files"], max_files=3)
            lines.append("Representative files:")
            for meta in representative:
                lines.append(f"- `{meta['relative_path']}` ({meta['rows']} rows, {meta['columns']} columns)")
            lines.append("")
        else:
            lines.append("No supported data files discovered for this dataset.")
            lines.append("")

    lines.append("## Potential Join Keys")
    lines.append("")
    join_rows = build_join_candidates(dataset_results)
    if not join_rows:
        lines.append("_No robust cross-dataset join candidates detected from available tabular files._")
        lines.append("")
    else:
        lines.append("| Dataset A/File | Dataset B or C/File | Join Key | Left Column | Right Column |")
        lines.append("|---|---|---|---|---|")
        for row in join_rows[:120]:
            left = f"{row['dataset_left']} / {row['file_left']}"
            right = f"{row['dataset_right']} / {row['file_right']}"
            lines.append(
                f"| {markdown_escape(left)} | {markdown_escape(right)} | "
                f"{markdown_escape(row['join_key'])} | "
                f"{markdown_escape(row['left_column'])} | "
                f"{markdown_escape(row['right_column'])} |"
            )
        if len(join_rows) > 120:
            lines.append("")
            lines.append(f"_Truncated: showing 120 of {len(join_rows)} inferred join candidates._")
            lines.append("")

    lines.append("## Possible Integration Strategy")
    lines.append("")
    lines.append(
        "1. Use Dataset A player-level tables as the primary backbone because they contain "
        "player identifiers, market values, profiles, and performance history."
    )
    lines.append(
        "2. Join Dataset B transfers on `player_id` and `season` where available, and use "
        "`player_name` as a fallback key with careful standardization."
    )
    lines.append(
        "3. Align team context using `team_id` / `team_name` and season context for transfer windows."
    )
    lines.append(
        "4. Incorporate Dataset C tabular files if present; otherwise treat Dataset C as "
        "methodological reference for modeling choices and engineered features."
    )
    lines.append(
        "5. Build a player-season analytical mart with one record per player-season and aggregated metrics "
        "from performances, transfer events, and market value observations."
    )
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def find_best_source_for_feature(
    dataset_results: dict[str, dict[str, Any]],
    preferred_dataset_order: list[str],
    canonical_feature: str,
) -> tuple[str, str]:
    for dataset_label in preferred_dataset_order:
        payload = dataset_results.get(dataset_label, {})
        for meta in payload.get("files", []):
            if meta.get("load_error"):
                continue
            mapped = canonical_column_map(meta.get("column_names", []))
            if canonical_feature in mapped:
                return dataset_label, meta["relative_path"]
    return "Not found", "N/A"


def build_unified_schema_markdown(dataset_results: dict[str, dict[str, Any]]) -> str:
    lines: list[str] = ["# Unified Player-Level Dataset Schema", ""]

    lines.append("## Target Variable")
    lines.append("")
    lines.append("market_value")
    lines.append("")

    lines.append("## Entity")
    lines.append("")
    lines.append("Player-season level dataset")
    lines.append("")

    proposed = [
        ("player_id", "Stable player identifier for joins", "player_id"),
        ("player_name", "Player name", "player_name"),
        ("season", "Season of observation", "season"),
        ("age", "Player age in season/transfer window", "age"),
        ("position", "Primary playing position", "position"),
        ("team_id", "Team/club identifier", "team_id"),
        ("team_name", "Team/club name", "team_name"),
        ("league", "League or competition context", "league"),
        ("goals", "Goals scored (aggregated player-season)", "goals"),
        ("assists", "Assists (aggregated player-season)", "assists"),
        ("minutes_played", "Minutes played (aggregated player-season)", "minutes_played"),
        ("transfer_fee", "Transfer fee amount", "transfer_fee"),
        ("market_value", "Observed market value", "market_value"),
    ]

    lines.append("## Proposed schema")
    lines.append("")
    lines.append("| Column | Description | Source Dataset |")
    lines.append("|---|---|---|")

    for column, description, canonical in proposed:
        source_dataset, source_file = find_best_source_for_feature(
            dataset_results=dataset_results,
            preferred_dataset_order=["Dataset A", "Dataset B", "Dataset C"],
            canonical_feature=canonical,
        )
        source = f"{source_dataset} ({source_file})"

        if canonical in {"goals", "assists", "minutes_played"}:
            # These are highly likely in player performances from Dataset A.
            if source_dataset == "Not found":
                source = "Dataset A (player_performances expected)"
        lines.append(f"| {column} | {description} | {markdown_escape(source)} |")

    lines.append("")
    lines.append("## Feature categories")
    lines.append("")
    lines.append("- Player attributes")
    lines.append("- Performance metrics")
    lines.append("- Team context")
    lines.append("- Transfer market information")
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append(
        "The unified schema is designed for downstream structuring and modeling. "
        "At this stage it is a target design, not a cleaned production table."
    )
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def analyze_all_datasets() -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for dataset_label, dataset_root in DATASET_DIRS.items():
        log_info(f"Discovering files in {dataset_label}: {dataset_root}")
        if not dataset_root.exists():
            log_warn(f"Dataset folder missing: {dataset_root}")
            results[dataset_label] = {
                "folder_name": dataset_root.name,
                "root": dataset_root,
                "files": [],
            }
            continue

        data_files = discover_data_files(dataset_root)
        log_info(f"Found {len(data_files)} supported data files in {dataset_label}")

        file_metas: list[dict[str, Any]] = []
        for idx, data_file in enumerate(data_files, start=1):
            log_info(f"[{dataset_label}] Profiling file {idx}/{len(data_files)}: {data_file.name}")
            file_metas.append(extract_file_metadata(data_file, dataset_root))

        results[dataset_label] = {
            "folder_name": dataset_root.name,
            "root": dataset_root,
            "files": file_metas,
        }
    return results


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    log_info(f"Wrote {path} ({len(text):,} chars)")


def main() -> None:
    log_info("Starting dataset analysis pipeline.")
    results = analyze_all_datasets()

    dataset_structure_md = build_dataset_structure_markdown(results)
    dataset_relationship_md = build_dataset_relationship_markdown(results)
    unified_schema_md = build_unified_schema_markdown(results)

    write_text(PROJECT_ROOT / "dataset_structure.md", dataset_structure_md)
    write_text(PROJECT_ROOT / "dataset_relationship.md", dataset_relationship_md)
    write_text(PROJECT_ROOT / "unified_player_schema.md", unified_schema_md)
    log_info("Dataset analysis pipeline completed successfully.")


if __name__ == "__main__":
    main()
