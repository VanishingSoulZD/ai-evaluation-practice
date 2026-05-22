#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ENTITY_TYPES = ["PER", "ORG", "LOC", "TIME"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day6: Python 基础复习与 Pandas/NumPy 数据处理练习")
    parser.add_argument("input_file", type=Path, help="Day5/历史标注数据 CSV 或 Excel")
    parser.add_argument("--output-dir", type=Path, default=Path("reports/day6_practice"), help="输出目录")
    parser.add_argument("--id-col", default="ID")
    parser.add_argument("--task-col", default="任务类型")
    parser.add_argument("--text-col", default="原始文本")
    parser.add_argument("--label-col", default="标注结果")
    return parser.parse_args()


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV/XLSX 文件")


def python_basics_demo() -> dict[str, object]:
    numbers = [1, 2, 2, 3, 5, 8]
    unique_sorted = sorted(set(numbers))
    squares = [n * n for n in unique_sorted]
    num_map = {n: n * n for n in unique_sorted}

    sentence = "  Python Data Processing Day6  "
    normalized = sentence.strip().lower().replace(" ", "_")
    vowel_count = sum(ch in "aeiou" for ch in normalized)

    total = 0
    for value in unique_sorted:
        if value % 2 == 0:
            total += value

    def scale(x: int, factor: int = 10) -> int:
        return x * factor

    return {
        "unique_numbers": unique_sorted,
        "squares": squares,
        "num_map": num_map,
        "normalized_text": normalized,
        "vowel_count": vowel_count,
        "sum_even_numbers": total,
        "scale_demo": scale(3),
    }


def extract_entity_tags(label_text: str) -> list[str]:
    if not isinstance(label_text, str):
        return []
    tags = []
    for entity_type in ENTITY_TYPES:
        if re.search(rf"\b{entity_type}\s*:", label_text):
            tags.append(entity_type)
    return tags


def build_pandas_outputs(df: pd.DataFrame, id_col: str, task_col: str, text_col: str, label_col: str) -> dict[str, pd.DataFrame]:
    data = df.copy()
    for col in [id_col, task_col, text_col, label_col]:
        if col not in data.columns:
            print(f"[WARN] 缺失列 {col}，将使用空列占位继续处理。")
            data[col] = ""

    data[label_col] = data[label_col].fillna("").astype(str)
    data[text_col] = data[text_col].fillna("").astype(str)

    raw_label_tokens = data[label_col].str.findall(r"\b[A-Z]{3,}\b")
    known_tokens = {"POS", "NEG", "NEU", "PER", "ORG", "LOC", "TIME"}
    unknown_tokens = sorted({token for tokens in raw_label_tokens for token in tokens if token not in known_tokens})
    if unknown_tokens:
        print(f"[WARN] 检测到未识别标签: {unknown_tokens}")

    data["text_len"] = data[text_col].map(len)
    data["task_group"] = data[task_col].apply(lambda x: "分类" if "分类" in str(x) else ("实体" if "实体" in str(x) else "其他"))
    data["has_sentiment"] = data[label_col].str.contains(r"\b(POS|NEG|NEU)\b", regex=True)
    data["entity_tags"] = data[label_col].apply(extract_entity_tags)

    task_stats = (
        data.groupby("task_group", as_index=False)
        .agg(samples=(id_col, "count"), avg_text_len=("text_len", "mean"), sentiment_rows=("has_sentiment", "sum"))
        .sort_values("samples", ascending=False)
    )

    entity_exploded = data[[id_col, "entity_tags"]].explode("entity_tags")
    entity_exploded = entity_exploded.dropna(subset=["entity_tags"])
    entity_dist = (
        entity_exploded.groupby("entity_tags", as_index=False)
        .agg(count=(id_col, "count"))
        .rename(columns={"entity_tags": "entity_label"})
        .sort_values("count", ascending=False)
    )

    task_stats["key"] = 1
    entity_dist["key"] = 1
    merged_view = pd.merge(task_stats, entity_dist, on="key", how="outer").drop(columns=["key"])

    label_counts = (
        data[label_col]
        .str.extract(r"\b(POS|NEG|NEU)\b", expand=False)
        .fillna("UNLABELED")
        .value_counts(dropna=False)
        .rename_axis("label")
        .reset_index(name="count")
    )
    label_counts["ratio"] = label_counts["count"] / max(len(data), 1)

    unlabeled_count = int(label_counts.loc[label_counts["label"] == "UNLABELED", "count"].sum())
    print(f"[INFO] 未标注样本数量(UNLABELED): {unlabeled_count}")

    duplicate_stats = pd.DataFrame(
        [
            {"metric": "total_rows", "value": int(len(data))},
            {"metric": "duplicate_id_rows", "value": int(data.duplicated(subset=[id_col]).sum())},
            {"metric": "duplicate_text_rows", "value": int(data.duplicated(subset=[text_col]).sum())},
        ]
    )

    return {
        "cleaned_data": data,
        "task_stats": task_stats,
        "entity_distribution": entity_dist,
        "task_entity_merged": merged_view,
        "label_distribution": label_counts,
        "duplicate_stats": duplicate_stats,
    }


def build_numpy_outputs(df: pd.DataFrame) -> dict[str, object]:
    text_len = df["text_len"].to_numpy(dtype=np.int64)
    ones = np.ones_like(text_len)
    plus_five = text_len + 5
    std_value = text_len.std()
    if std_value == 0:
        print("[WARN] text_len 标准差为 0，归一化将使用 1 作为分母。")
    normalized = (text_len - text_len.mean()) / (std_value if std_value else 1)
    long_text_mask = text_len >= np.median(text_len)

    return {
        "array_shape": list(text_len.shape),
        "slice_first_5": text_len[:5].tolist(),
        "broadcast_plus_five_first_5": plus_five[:5].tolist(),
        "mask_long_text_count": int(long_text_mask.sum()),
        "aggregations": {
            "sum": int(np.sum(text_len)),
            "mean": float(np.mean(text_len)),
            "max": int(np.max(text_len)) if text_len.size else 0,
            "min": int(np.min(text_len)) if text_len.size else 0,
        },
        "vector_add_demo_first_5": (text_len[:5] + ones[:5]).tolist(),
        "normalized_first_5": np.round(normalized[:5], 4).tolist(),
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = load_table(args.input_file)

    basics = python_basics_demo()
    pandas_outputs = build_pandas_outputs(df, args.id_col, args.task_col, args.text_col, args.label_col)
    numpy_outputs = build_numpy_outputs(pandas_outputs["cleaned_data"])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for name, table in pandas_outputs.items():
        table.to_csv(args.output_dir / f"{name}_{timestamp}.csv", index=False, encoding="utf-8-sig")

    (args.output_dir / f"python_basics_demo_{timestamp}.json").write_text(json.dumps(basics, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / f"numpy_summary_{timestamp}.json").write_text(json.dumps(numpy_outputs, ensure_ascii=False, indent=2), encoding="utf-8")

    total_rows = int(len(pandas_outputs["cleaned_data"]))
    dup_id_rows = int(pandas_outputs["cleaned_data"].duplicated(subset=[args.id_col]).sum())
    dup_text_rows = int(pandas_outputs["cleaned_data"].duplicated(subset=[args.text_col]).sum())
    unlabeled_rows = int(pandas_outputs["label_distribution"].loc[pandas_outputs["label_distribution"]["label"] == "UNLABELED", "count"].sum())

    print(f"[INFO] 样本总数: {total_rows}")
    print(f"[INFO] 重复 ID 数量: {dup_id_rows}")
    print(f"[INFO] 重复文本数量: {dup_text_rows}")
    print(f"[INFO] 未标注样本数量: {unlabeled_rows}")
    print(f"Day6 练习完成：输出目录 {args.output_dir}，文件时间戳 {timestamp}")


if __name__ == "__main__":
    main()
