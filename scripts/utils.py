#!/usr/bin/env python3
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ENTITY_ORDER = ["PER", "ORG", "LOC", "TIME"]
ENTITY_PATTERN = re.compile(r"(PER|ORG|LOC|TIME)\s*[:：]\s*([^,，;；|]+)")
BIO_PATTERN = re.compile(r"\((B|I|O)(?:-([A-Z]+))?\)")


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
