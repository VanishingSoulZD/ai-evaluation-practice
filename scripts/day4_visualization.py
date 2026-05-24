#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


import pandas as pd


from scripts.utils import (
    extract_bio_matrix,
    extract_entity_counts,
    plot_bio_heatmap,
    plot_entity_bar,
    plot_sentiment_hist,
    setup_matplotlib_style,
)

SENTIMENT_ORDER = ["POS", "NEG", "NEU"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 4 标注数据可视化脚本")
    parser.add_argument("input_file", type=Path, help="输入文件路径，支持 CSV 或 XLSX")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/day4_visualization"),
        help="输出目录",
    )
    parser.add_argument("--id-col", default="ID")
    parser.add_argument("--task-col", default="任务类型")
    parser.add_argument("--text-col", default="原始文本")
    parser.add_argument("--label-col", default="标注结果")
    parser.add_argument(
        "--excel", action="store_true", help="同时输出 Excel 统计表（需 openpyxl）"
    )
    return parser.parse_args()


def load_data(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV 或 Excel 文件")


def extract_sentiment_counts(df: pd.DataFrame, label_col: str) -> pd.Series:
    labels = df[label_col].fillna("").astype(str).str.upper()
    counts = pd.Series(
        {lb: labels.str.contains(rf"\b{lb}\b").sum() for lb in SENTIMENT_ORDER},
        dtype="int64",
    )
    return counts


def build_summary_table(
    df: pd.DataFrame,
    id_col: str,
    text_col: str,
    sentiment_counts: pd.Series,
    entity_counts: pd.Series,
) -> pd.DataFrame:
    missing_cells = int(df.isna().sum().sum())
    duplicate_id_rows = (
        int(df.duplicated(subset=[id_col]).sum()) if id_col in df.columns else 0
    )
    duplicate_text_rows = (
        int(df.duplicated(subset=[text_col]).sum()) if text_col in df.columns else 0
    )

    rows = [
        {"metric": "total_samples", "value": int(len(df))},
        {"metric": "missing_cells", "value": missing_cells},
        {"metric": "duplicate_id_rows", "value": duplicate_id_rows},
        {"metric": "duplicate_text_rows", "value": duplicate_text_rows},
    ]
    rows.extend(
        {"metric": f"sentiment_{k}", "value": int(v)}
        for k, v in sentiment_counts.items()
    )
    rows.extend(
        {"metric": f"entity_{k}", "value": int(v)} for k, v in entity_counts.items()
    )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = load_data(args.input_file)
    required_cols = [args.id_col, args.task_col, args.text_col, args.label_col]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要列: {missing_cols}")

    sentiment_counts = extract_sentiment_counts(df, args.label_col)
    entity_counts = extract_entity_counts(df, args.label_col)
    bio_matrix = extract_bio_matrix(df, args.label_col)
    summary_df = build_summary_table(
        df, args.id_col, args.text_col, sentiment_counts, entity_counts
    )

    sentiment_counts.rename_axis("label").reset_index(name="count").to_csv(
        args.output_dir / "sentiment_distribution.csv",
        index=False,
        encoding="utf-8-sig",
    )
    entity_counts.rename_axis("label").reset_index(name="count").to_csv(
        args.output_dir / "entity_distribution.csv", index=False, encoding="utf-8-sig"
    )
    bio_matrix.to_csv(args.output_dir / "bio_distribution.csv", encoding="utf-8-sig")
    summary_df.to_csv(
        args.output_dir / "summary_stats.csv", index=False, encoding="utf-8-sig"
    )

    if args.excel:
        excel_path = args.output_dir / "day4_visualization_stats.xlsx"
        with pd.ExcelWriter(excel_path) as writer:
            summary_df.to_excel(writer, sheet_name="summary", index=False)
            sentiment_counts.rename_axis("label").reset_index(name="count").to_excel(
                writer, sheet_name="sentiment", index=False
            )
            entity_counts.rename_axis("label").reset_index(name="count").to_excel(
                writer, sheet_name="entity", index=False
            )
            bio_matrix.to_excel(writer, sheet_name="bio")

    plot_sentiment_hist(sentiment_counts, args.output_dir)
    plot_entity_bar(entity_counts, args.output_dir)
    plot_bio_heatmap(bio_matrix, args.output_dir)

    print(f"完成可视化输出，目录: {args.output_dir}")


if __name__ == "__main__":
    # uv run python -m scripts.day4_visualization data/day02_annotation.csv --excel
    # uv run python -m scripts.day4_visualization data/day02_annotation.xlsx --excel
    setup_matplotlib_style()
    main()
