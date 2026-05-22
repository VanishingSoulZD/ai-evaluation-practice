#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

SENTIMENT_ORDER = ["POS", "NEG", "NEU"]
ENTITY_ORDER = ["PER", "ORG", "LOC", "TIME"]
ENTITY_PATTERN = re.compile(r"(PER|ORG|LOC|TIME)\s*[:：]\s*([^,，;；|]+)")
BIO_PATTERN = re.compile(r"\((B|I|O)(?:-([A-Z]+))?\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 4 标注数据可视化脚本")
    parser.add_argument("input_file", type=Path, help="输入文件路径，支持 CSV 或 XLSX")
    parser.add_argument("--output-dir", type=Path, default=Path("reports/day4_visualization"), help="输出目录")
    parser.add_argument("--id-col", default="ID")
    parser.add_argument("--task-col", default="任务类型")
    parser.add_argument("--text-col", default="原始文本")
    parser.add_argument("--label-col", default="标注结果")
    parser.add_argument("--excel", action="store_true", help="同时输出 Excel 统计表（需 openpyxl）")
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
    counts = pd.Series({lb: labels.str.contains(rf"\b{lb}\b").sum() for lb in SENTIMENT_ORDER}, dtype="int64")
    return counts


def extract_entity_counts(df: pd.DataFrame, label_col: str) -> pd.Series:
    counter: Counter[str] = Counter()
    for text in df[label_col].fillna("").astype(str):
        for key, _ in ENTITY_PATTERN.findall(text):
            counter[key] += 1
    return pd.Series({key: counter.get(key, 0) for key in ENTITY_ORDER}, dtype="int64")


def extract_bio_matrix(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    bio_counter: dict[str, Counter[str]] = {prefix: Counter() for prefix in ["B", "I", "O"]}
    for text in df[label_col].fillna("").astype(str):
        for prefix, entity_type in BIO_PATTERN.findall(text):
            normalized = entity_type if entity_type else "NONE"
            bio_counter[prefix][normalized] += 1

    all_types = sorted({etype for c in bio_counter.values() for etype in c.keys()}) or ["NONE"]
    matrix = pd.DataFrame(index=["B", "I", "O"], columns=all_types, data=0)
    for prefix, counts in bio_counter.items():
        for etype, value in counts.items():
            matrix.loc[prefix, etype] = value
    return matrix.astype(int)


def plot_sentiment_hist(counts: pd.Series, output_dir: Path) -> None:
    plt.figure(figsize=(8, 5))
    sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette="Set2", legend=False)
    plt.title("文本分类标签分布")
    plt.xlabel("情感标签")
    plt.ylabel("样本数量")
    for idx, val in enumerate(counts.values):
        plt.text(idx, val, str(int(val)), ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(output_dir / "sentiment_histogram.png", dpi=180)
    plt.close()


def plot_entity_bar(counts: pd.Series, output_dir: Path) -> None:
    plt.figure(figsize=(8, 5))
    sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette="Blues_d", legend=False)
    plt.title("实体标签出现频率")
    plt.xlabel("实体标签")
    plt.ylabel("出现次数")
    for idx, val in enumerate(counts.values):
        plt.text(idx, val, str(int(val)), ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(output_dir / "entity_bar_chart.png", dpi=180)
    plt.close()


def plot_bio_heatmap(matrix: pd.DataFrame, output_dir: Path) -> None:
    plt.figure(figsize=(10, 4))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="YlOrRd", cbar_kws={"label": "标签数量"})
    plt.title("BIO 标签分布热力图")
    plt.xlabel("实体类型")
    plt.ylabel("BIO 前缀")
    plt.tight_layout()
    plt.savefig(output_dir / "bio_heatmap.png", dpi=180)
    plt.close()


def build_summary_table(
    df: pd.DataFrame,
    id_col: str,
    text_col: str,
    sentiment_counts: pd.Series,
    entity_counts: pd.Series,
) -> pd.DataFrame:
    missing_cells = int(df.isna().sum().sum())
    duplicate_id_rows = int(df.duplicated(subset=[id_col]).sum()) if id_col in df.columns else 0
    duplicate_text_rows = int(df.duplicated(subset=[text_col]).sum()) if text_col in df.columns else 0

    rows = [
        {"metric": "total_samples", "value": int(len(df))},
        {"metric": "missing_cells", "value": missing_cells},
        {"metric": "duplicate_id_rows", "value": duplicate_id_rows},
        {"metric": "duplicate_text_rows", "value": duplicate_text_rows},
    ]
    rows.extend({"metric": f"sentiment_{k}", "value": int(v)} for k, v in sentiment_counts.items())
    rows.extend({"metric": f"entity_{k}", "value": int(v)} for k, v in entity_counts.items())
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
    summary_df = build_summary_table(df, args.id_col, args.text_col, sentiment_counts, entity_counts)

    sentiment_counts.rename_axis("label").reset_index(name="count").to_csv(
        args.output_dir / "sentiment_distribution.csv", index=False, encoding="utf-8-sig"
    )
    entity_counts.rename_axis("label").reset_index(name="count").to_csv(
        args.output_dir / "entity_distribution.csv", index=False, encoding="utf-8-sig"
    )
    bio_matrix.to_csv(args.output_dir / "bio_distribution.csv", encoding="utf-8-sig")
    summary_df.to_csv(args.output_dir / "summary_stats.csv", index=False, encoding="utf-8-sig")

    if args.excel:
        excel_path = args.output_dir / "day4_visualization_stats.xlsx"
        with pd.ExcelWriter(excel_path) as writer:
            summary_df.to_excel(writer, sheet_name="summary", index=False)
            sentiment_counts.rename_axis("label").reset_index(name="count").to_excel(writer, sheet_name="sentiment", index=False)
            entity_counts.rename_axis("label").reset_index(name="count").to_excel(writer, sheet_name="entity", index=False)
            bio_matrix.to_excel(writer, sheet_name="bio")

    sns.set_theme(style="whitegrid")
    plot_sentiment_hist(sentiment_counts, args.output_dir)
    plot_entity_bar(entity_counts, args.output_dir)
    plot_bio_heatmap(bio_matrix, args.output_dir)

    print(f"完成可视化输出，目录: {args.output_dir}")


if __name__ == "__main__":
    main()
