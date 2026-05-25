#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

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
DEFAULT_RULES: dict[str, list[str]] = {
    "PER": [
        r"王\S{1}",
        r"李\S{1}",
        r"刘\S{1}",
        r"张\S{1}",
        r"赵\S{1}",
        r"陈\S{1}",
        r"小张",
        r"小王",
        r"小李",
    ],
    "ORG": [
        r"腾讯",
        r"华为",
        r"OpenAI",
        r"阿里巴巴",
        r"字节跳动",
        r"北京大学",
        r"清华大学",
        r"复旦大学",
        r"微软亚洲研究院",
    ],
    "LOC": [
        r"北京",
        r"上海",
        r"深圳",
        r"广州",
        r"杭州",
        r"成都",
        r"南京",
        r"武汉",
        r"香港",
        r"旧金山",
        r"台北",
    ],
    "TIME": [
        r"今天",
        r"昨天",
        r"明天",
        r"周[一二三四五六日天]",
        r"下周\S*",
        r"本周\S*",
        r"\d{4}年\d{1,2}月\d{1,2}日",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day5: 标注 → 分析 → 可视化")
    parser.add_argument("input_file", type=Path, help="输入文件路径（CSV/XLSX）")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/day5_pipeline"),
        help="输出目录",
    )
    parser.add_argument(
        "--rules-file", type=Path, default=None, help="实体抽取规则文件（JSON）"
    )
    parser.add_argument("--id-col", default="ID")
    parser.add_argument("--task-col", default="任务类型")
    parser.add_argument("--text-col", default="原始文本")
    parser.add_argument("--label-col", default="标注结果")
    parser.add_argument("--issue-col", default="发现的问题")
    parser.add_argument("--max-samples", type=int, default=50)
    parser.add_argument("--excel", action="store_true", help="是否输出 Excel")
    return parser.parse_args()


def load_data(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig")
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV/XLSX 输入")


def load_rules(path: Path | None) -> dict[str, list[str]]:
    if path is None:
        return DEFAULT_RULES
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    rules: dict[str, list[str]] = {}
    for tag in ["PER", "ORG", "LOC", "TIME"]:
        raw = payload.get(tag, [])
        rules[tag] = [str(x) for x in raw] if isinstance(raw, list) else []
    return rules


def classify_text(text: str) -> str:
    pos_kw = ["满意", "不错", "方便", "专业", "提升", "修好了", "感谢"]
    neg_kw = ["慢", "差", "找不到", "敷衍", "没", "问题"]
    if any(k in text for k in pos_kw):
        return "POS"
    if any(k in text for k in neg_kw):
        return "NEG"
    return "NEU"


def extract_entities_from_text(text: str, rules: dict[str, list[str]]) -> list[str]:
    entities: list[str] = []
    for tag in ["PER", "ORG", "LOC", "TIME"]:
        for pattern in rules.get(tag, []):
            for value in re.findall(pattern, text):
                entities.append(f"{tag}: {value}")
    return entities


def annotate_missing(
    df: pd.DataFrame,
    task_col: str,
    text_col: str,
    label_col: str,
    issue_col: str,
    rules: dict[str, list[str]],
) -> pd.DataFrame:
    out = df.copy()
    if issue_col not in out.columns:
        out[issue_col] = ""
    out[label_col] = out[label_col].fillna("")
    missing_mask = out[label_col].astype(str).str.strip().eq("")

    def build_label(row: pd.Series) -> tuple[str, str]:
        task = str(row.get(task_col, ""))
        text = str(row.get(text_col, ""))
        parts: list[str] = []
        if "分类" in task:
            parts.append(classify_text(text))
        if "实体" in task or "抽取" in task:
            entities = extract_entities_from_text(text, rules)
            if entities:
                parts.append("; ".join(entities))
        return (
            "; ".join(parts) if parts else "NEU",
            "自动补标：原标注缺失，依据 Day1-2 规则启发式填充。",
        )

    filled = out.loc[missing_mask].apply(build_label, axis=1, result_type="expand")
    if not filled.empty:
        out.loc[missing_mask, label_col] = filled[0]
        out.loc[missing_mask, issue_col] = filled[1]
    return out


def extract_sentiment_counts(df: pd.DataFrame, label_col: str) -> pd.Series:
    labels = df[label_col].fillna("").astype(str).str.upper()
    return pd.Series(
        {lb: labels.str.contains(rf"\b{lb}\b").sum() for lb in SENTIMENT_ORDER},
        dtype="int64",
    )


def build_summary(
    df: pd.DataFrame, id_col: str, text_col: str, label_col: str
) -> pd.DataFrame:
    sentiment_counts = extract_sentiment_counts(df, label_col)
    entity_counts = extract_entity_counts(df, label_col)
    rows = [
        {"metric": "total_samples", "value": int(len(df))},
        {"metric": "missing_cells", "value": int(df.isna().sum().sum())},
        {
            "metric": "duplicate_id_rows",
            "value": int(df.duplicated(subset=[id_col]).sum())
            if id_col in df.columns
            else 0,
        },
        {
            "metric": "duplicate_text_rows",
            "value": int(df.duplicated(subset=[text_col]).sum())
            if text_col in df.columns
            else 0,
        },
    ]
    rows += [
        {"metric": f"sentiment_{k}", "value": int(v)}
        for k, v in sentiment_counts.items()
    ]
    rows += [
        {"metric": f"entity_{k}", "value": int(v)} for k, v in entity_counts.items()
    ]
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rules = load_rules(args.rules_file)
    df = load_data(args.input_file).head(args.max_samples)
    if args.label_col not in df.columns:
        df[args.label_col] = ""

    required_cols = [args.id_col, args.task_col, args.text_col]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要列: {missing_cols}")

    annotated = annotate_missing(
        df, args.task_col, args.text_col, args.label_col, args.issue_col, rules
    )
    sentiment_counts = extract_sentiment_counts(annotated, args.label_col)
    entity_counts = extract_entity_counts(annotated, args.label_col)
    bio_matrix = extract_bio_matrix(annotated, args.label_col)
    summary = build_summary(annotated, args.id_col, args.text_col, args.label_col)

    log_df = annotated[
        [
            c
            for c in [args.id_col, args.text_col, args.label_col, args.issue_col]
            if c in annotated.columns
        ]
    ].copy()
    log_df.to_csv(
        args.output_dir / "annotation_log.csv", index=False, encoding="utf-8-sig"
    )
    summary.to_csv(
        args.output_dir / "summary_stats.csv", index=False, encoding="utf-8-sig"
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

    if args.excel:
        with pd.ExcelWriter(
            args.output_dir / "day5_stats.xlsx", engine="openpyxl"
        ) as writer:
            log_df.to_excel(writer, sheet_name="annotation_log", index=False)
            summary.to_excel(writer, sheet_name="summary", index=False)
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

    print(
        f"Day 5 流程完成：已处理 {len(annotated)} 条样本，输出目录：{args.output_dir}"
    )


if __name__ == "__main__":
    # uv run python -m scripts.day5_annotation_analysis_pipeline data/day02_annotation.csv --excel
    # uv run python -m scripts.day5_annotation_analysis_pipeline data/day02_annotation.xlsx --excel
    setup_matplotlib_style()
    main()
