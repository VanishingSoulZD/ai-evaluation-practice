import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

MAX_ROWS = 50


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="计算双人标注的 Cohen's Kappa（MVP）。")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("reports/day35_disagreement_analysis.csv"),
        help="输入文件路径（支持 .csv 或 .jsonl，默认: reports/day35_disagreement_analysis.csv）",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=MAX_ROWS,
        help=f"最多读取前 N 条样本（默认: {MAX_ROWS}）",
    )
    return parser.parse_args()


def _load_csv(path: Path, max_rows: int) -> pd.DataFrame:
    return pd.read_csv(path, nrows=max_rows)


def _load_jsonl(path: Path, max_rows: int) -> pd.DataFrame:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_rows:
                break
            text = line.strip()
            if not text:
                continue
            records.append(json.loads(text))
    return pd.DataFrame(records)


def _validate_base(df: pd.DataFrame) -> None:
    if "sample_id" not in df.columns:
        raise ValueError("输入数据缺少 sample_id 列")
    if df["sample_id"].isna().any() or (df["sample_id"].astype(str).str.strip() == "").any():
        raise ValueError("存在空 sample_id")


def _from_disagreement_report(df: pd.DataFrame) -> tuple[list[str], list[str], pd.DataFrame]:
    if "label_pair" not in df.columns:
        raise ValueError("未找到 label_pair 列，无法从 day35 分歧报告提取标签")

    label_split = df["label_pair"].astype(str).str.split("|", n=1, expand=True)
    if label_split.shape[1] != 2:
        raise ValueError("label_pair 格式不正确，预期为 labelA|labelB")

    aligned = pd.DataFrame(
        {
            "sample_id": df["sample_id"],
            "label_A": label_split[0].astype(str).str.strip(),
            "label_B": label_split[1].astype(str).str.strip(),
        }
    )
    aligned = aligned[(aligned["label_A"] != "") & (aligned["label_B"] != "")]
    aligned = aligned[(aligned["label_A"] != "MISSING") & (aligned["label_B"] != "MISSING")]

    if aligned.empty:
        raise ValueError("无可用对齐样本（标签为空或 MISSING）")

    labels_a = aligned["label_A"].tolist()
    labels_b = aligned["label_B"].tolist()
    return labels_a, labels_b, aligned


def _from_annotation_table(df: pd.DataFrame) -> tuple[list[str], list[str], pd.DataFrame]:
    required_cols = {"sample_id", "annotator", "label"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"缺少必要列: {', '.join(sorted(missing))}")

    clean = df.copy()
    clean["label"] = clean["label"].astype(str).str.strip()
    clean = clean[clean["label"] != ""]

    if clean.empty:
        raise ValueError("无有效标签数据")

    annotators = clean["annotator"].dropna().astype(str).unique().tolist()
    if len(annotators) < 2:
        raise ValueError("至少需要两个 annotator")

    a_name, b_name = annotators[:2]
    a_df = (
        clean[clean["annotator"].astype(str) == a_name][["sample_id", "label"]]
        .drop_duplicates(subset=["sample_id"], keep="first")
        .rename(columns={"label": "label_A"})
    )
    b_df = (
        clean[clean["annotator"].astype(str) == b_name][["sample_id", "label"]]
        .drop_duplicates(subset=["sample_id"], keep="first")
        .rename(columns={"label": "label_B"})
    )

    aligned = a_df.merge(b_df, how="inner", on="sample_id")
    aligned = aligned[(aligned["label_A"] != "") & (aligned["label_B"] != "")]

    if aligned.empty:
        raise ValueError("按 sample_id 对齐后无有效样本")

    return aligned["label_A"].tolist(), aligned["label_B"].tolist(), aligned


def load_and_align(path: Path, max_rows: int) -> tuple[list[str], list[str], pd.DataFrame]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = _load_csv(path, max_rows)
    elif suffix == ".jsonl":
        df = _load_jsonl(path, max_rows)
    else:
        raise ValueError("仅支持 .csv 或 .jsonl")

    _validate_base(df)

    if "label_pair" in df.columns:
        return _from_disagreement_report(df)
    return _from_annotation_table(df)


def main() -> None:
    args = parse_args()
    labels_a, labels_b, aligned = load_and_align(args.input, args.max_rows)

    sample_count = len(aligned)
    agreement_count = sum(a == b for a, b in zip(labels_a, labels_b))
    raw_agreement = agreement_count / sample_count
    overall_kappa = cohen_kappa_score(labels_a, labels_b)

    print(f"input_file: {args.input}")
    print(f"sample_count: {sample_count}")
    print(f"raw_agreement: {raw_agreement:.4f}")
    print(f"overall_kappa: {overall_kappa:.4f}")


if __name__ == "__main__":
    main()
