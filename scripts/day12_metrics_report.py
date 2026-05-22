#!/usr/bin/env python3
"""Day 12: metrics report generation (CSV + PNG).

This script converts Day 11 ``TextMetrics.compute_all()`` outputs into a Pandas
DataFrame, writes a CSV report, and renders a readable Matplotlib chart.

Features
--------
- Supports single sample (dict) and multi-sample (list[dict]) inputs.
- Handles empty input by emitting an empty table and a placeholder chart.
- Handles zero values safely.
- Reusable functions for integration into later automation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd

from day11_text_metrics import TextMetrics

METRIC_COLUMNS: list[str] = [
    "rouge_1",
    "rouge_2",
    "rouge_l",
    "bleu_1",
    "bleu_2",
    "accuracy",
    "win_rate_half_tie",
    "win_rate_no_tie_credit",
]


def normalize_metrics_input(metrics: dict[str, float] | Iterable[dict[str, float]]) -> pd.DataFrame:
    """Normalize metrics into a DataFrame with stable column order.

    Parameters
    ----------
    metrics : dict[str, float] | Iterable[dict[str, float]]
        Either one metrics dict from ``TextMetrics.compute_all()`` or multiple
        dict records.

    Returns
    -------
    pd.DataFrame
        DataFrame containing only Day 12 required columns. Missing values are
        filled with 0.0.
    """
    if isinstance(metrics, dict):
        records = [metrics]
    else:
        records = list(metrics)

    if not records:
        return pd.DataFrame(columns=METRIC_COLUMNS)

    df = pd.DataFrame(records)
    for column in METRIC_COLUMNS:
        if column not in df.columns:
            df[column] = 0.0

    df = df[METRIC_COLUMNS].fillna(0.0)
    return df.astype(float)


def save_metrics_csv(df: pd.DataFrame, output_csv: str | Path = "day12_metrics_report.csv") -> Path:
    """Save metrics DataFrame to CSV."""
    output_path = Path(output_csv)
    df.to_csv(output_path, index=False)
    return output_path


def plot_metrics(df: pd.DataFrame, output_png: str | Path = "day12_metrics_report.png") -> Path:
    """Render metrics chart for single or multiple samples.

    - Single sample: bar chart (x=metric names, y=metric value)
    - Multi sample: line chart with each metric as one colored line
    - Empty sample: placeholder chart with axis and hint text
    """
    output_path = Path(output_png)
    fig, ax = plt.subplots(figsize=(12, 6))

    if df.empty:
        ax.set_title("Day 12 Metrics Report (No Samples)")
        ax.set_xlabel("Metrics")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 1)
        ax.text(
            0.5,
            0.5,
            "No samples provided",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
    elif len(df) == 1:
        values = df.iloc[0]
        colors = plt.cm.tab10(range(len(METRIC_COLUMNS)))
        ax.bar(METRIC_COLUMNS, values, color=colors)
        ax.set_title("Day 12 Metrics Report (Single Sample)")
        ax.set_xlabel("Metric")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 1)
        ax.tick_params(axis="x", rotation=30)
    else:
        x = range(len(df))
        for metric in METRIC_COLUMNS:
            ax.plot(x, df[metric], marker="o", label=metric)
        ax.set_title("Day 12 Metrics Report (Multiple Samples)")
        ax.set_xlabel("Sample Index")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 1)
        ax.set_xticks(list(x))
        ax.legend(loc="upper right", ncol=2, fontsize=9)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def build_metrics_report(
    metrics: dict[str, float] | Iterable[dict[str, float]],
    output_csv: str | Path = "day12_metrics_report.csv",
    output_png: str | Path = "day12_metrics_report.png",
) -> tuple[pd.DataFrame, Path, Path]:
    """Build Day 12 report artifacts from metric dictionaries."""
    df = normalize_metrics_input(metrics)
    csv_path = save_metrics_csv(df, output_csv)
    png_path = plot_metrics(df, output_png)
    return df, csv_path, png_path


def main() -> None:
    """Generate demo Day 12 report directly using Day 11 TextMetrics."""
    single_metrics = TextMetrics(
        reference="the cat is on the mat",
        candidate="the cat sat on the mat",
        y_true=[1, 0, 1, 1, 0, 0, 1, 0],
        y_pred=[1, 1, 1, 1, 0, 0, 0, 0],
        wins=6,
        losses=3,
        ties=1,
    ).compute_all()

    # Demo includes multiple rows to show multi-sample compatibility.
    metrics_records = [
        single_metrics,
        TextMetrics("", "", [], [], 0, 0, 0).compute_all(),
    ]

    df, csv_path, png_path = build_metrics_report(metrics_records)
    print(f"rows={len(df)} columns={len(df.columns)}")
    print(f"csv={csv_path}")
    print(f"png={png_path}")


if __name__ == "__main__":
    main()
