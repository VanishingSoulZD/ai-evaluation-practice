#!/usr/bin/env python3
"""Day 13: automated batch processing for Day 11/12 metrics pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from scripts.day11_text_metrics import TextMetrics
    from scripts.day12_metrics_report import build_metrics_report
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from scripts.day11_text_metrics import TextMetrics
    from scripts.day12_metrics_report import build_metrics_report


REQUIRED_SAMPLE_FIELDS = {
    "reference",
    "candidate",
    "y_true",
    "y_pred",
    "wins",
    "losses",
    "ties",
}


def default_batches() -> list[list[dict[str, Any]]]:
    """Return built-in demo batches when no input directory is provided."""
    return [
        [
            {
                "reference": "the cat is on the mat",
                "candidate": "the cat sat on the mat",
                "y_true": [1, 0, 1, 1],
                "y_pred": [1, 1, 1, 0],
                "wins": 6,
                "losses": 3,
                "ties": 1,
            },
            {
                "reference": "a quick brown fox jumps",
                "candidate": "quick brown fox jumps high",
                "y_true": [0, 1, 1],
                "y_pred": [0, 1, 0],
                "wins": 4,
                "losses": 4,
                "ties": 2,
            },
        ],
        [
            {
                "reference": "machine learning improves prediction",
                "candidate": "machine learning improves forecasting",
                "y_true": [1, 1, 0, 0],
                "y_pred": [1, 1, 0, 1],
                "wins": 10,
                "losses": 2,
                "ties": 0,
            },
            {
                "reference": "",
                "candidate": "",
                "y_true": [],
                "y_pred": [],
                "wins": 0,
                "losses": 0,
                "ties": 0,
            },
        ],
        [
            {
                "reference": "data pipelines should be robust",
                "candidate": "robust data pipelines are important",
                "y_true": [1, 0, 1, 0, 1],
                "y_pred": [1, 0, 1, 0, 1],
                "wins": 7,
                "losses": 1,
                "ties": 2,
            }
        ],
    ]


def _coerce_int_list(value: Any, field_name: str) -> list[int]:
    if isinstance(value, list):
        return [int(v) for v in value]
    raise ValueError(f"{field_name} must be a list")


def validate_sample(sample: dict[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_SAMPLE_FIELDS - set(sample)
    if missing:
        raise ValueError(f"missing required fields: {sorted(missing)}")

    validated = {
        "reference": str(sample["reference"]),
        "candidate": str(sample["candidate"]),
        "y_true": _coerce_int_list(sample["y_true"], "y_true"),
        "y_pred": _coerce_int_list(sample["y_pred"], "y_pred"),
        "wins": int(sample["wins"]),
        "losses": int(sample["losses"]),
        "ties": int(sample["ties"]),
    }
    return validated


def load_batches_from_json(path: Path) -> list[list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return [data]
    if isinstance(data, list) and (not data or isinstance(data[0], list)):
        return data
    raise ValueError("JSON must be a list[sample] or list[list[sample]]")


def load_batches_from_csv(path: Path) -> list[list[dict[str, Any]]]:
    df = pd.read_csv(path)
    records = df.to_dict(orient="records")
    samples: list[dict[str, Any]] = []
    for row in records:
        row = dict(row)
        for key in ("y_true", "y_pred"):
            value = row.get(key, "[]")
            try:
                if isinstance(value, str):
                    row[key] = json.loads(value)
                elif isinstance(value, list):
                    row[key] = value
                else:
                    raise ValueError(f"{key} must be JSON string or list")
            except Exception:
                row[key] = []
        samples.append(row)
    return [samples]


def load_batches(input_dir: Path | None) -> list[list[dict[str, Any]]]:
    if input_dir is None:
        return default_batches()

    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"input dir not found: {input_dir}")

    batches: list[list[dict[str, Any]]] = []
    files = sorted([*input_dir.glob("*.json"), *input_dir.glob("*.csv")])
    for file_path in files:
        if file_path.suffix == ".json":
            batches.extend(load_batches_from_json(file_path))
        elif file_path.suffix == ".csv":
            batches.extend(load_batches_from_csv(file_path))

    return batches


def process_batch(batch: list[dict[str, Any]], batch_idx: int, logger: logging.Logger) -> tuple[list[dict[str, float]], int]:
    metrics_list: list[dict[str, float]] = []
    skipped = 0
    for sample_idx, sample in enumerate(batch):
        try:
            validated = validate_sample(sample)
            metrics = TextMetrics(**validated).compute_all()
            metrics_list.append(metrics)
        except Exception as exc:
            skipped += 1
            logger.warning("batch=%s sample=%s skipped: %s", batch_idx, sample_idx, exc)
    return metrics_list, skipped


def run_batch_pipeline(input_dir: Path | None, output_dir: Path, warn_log: Path | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("day13_batch_process")
    logger.handlers.clear()
    logger.setLevel(logging.WARNING)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("[WARN] %(message)s"))
    logger.addHandler(stream_handler)
    if warn_log is not None:
        warn_log.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(warn_log, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s [WARN] %(message)s"))
        logger.addHandler(file_handler)

    batches = load_batches(input_dir)
    total_samples = 0
    total_skipped = 0

    print(f"[INFO] loaded {len(batches)} batch(es)")
    for i, batch in enumerate(batches, start=1):
        print(f"[INFO] processing batch {i} with {len(batch)} sample(s)")
        total_samples += len(batch)
        metrics_list, skipped = process_batch(batch, i, logger)
        total_skipped += skipped
        csv_path = output_dir / f"batch_{i}_metrics.csv"
        png_path = output_dir / f"batch_{i}_metrics.png"
        _, csv_out, png_out = build_metrics_report(metrics_list, csv_path, png_path)
        print(f"[OK] batch {i}: csv={csv_out} png={png_out}")

    print(f"[INFO] total batches={len(batches)}, total samples={total_samples}, total skipped={total_skipped}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 13 batch processor for TextMetrics reports")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Input directory containing .json/.csv batch files. If omitted, built-in demo data is used.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/day13_batch"),
        help="Output directory for batch_{i}_metrics.csv and batch_{i}_metrics.png",
    )
    parser.add_argument(
        "--warn-log",
        type=Path,
        default=None,
        help="Optional log file path for warning messages.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_batch_pipeline(args.input_dir, args.output_dir, args.warn_log)


if __name__ == "__main__":
    main()
