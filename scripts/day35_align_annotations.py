import argparse
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"sample_id", "annotator", "label"}


def _validate_columns(df: pd.DataFrame, csv_path: Path) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"{csv_path} 缺少必要列: {missing_cols}")


def _warn_duplicates(df: pd.DataFrame, annotator_name: str) -> None:
    dup_mask = df.duplicated(subset=["sample_id"], keep=False)
    dup_count = int(dup_mask.sum())
    if dup_count:
        dup_ids = df.loc[dup_mask, "sample_id"].astype(str).head(10).tolist()
        print(
            "[WARNING] "
            f"annotator={annotator_name} 存在重复 sample_id: {dup_count} 条；"
            f"示例: {dup_ids}"
        )


def _warn_missing_ids(aligned: pd.DataFrame) -> None:
    only_a = aligned[aligned["label_B"].isna()]["sample_id"].astype(str).tolist()
    only_b = aligned[aligned["label_A"].isna()]["sample_id"].astype(str).tolist()
    if only_a:
        print(
            "[WARNING] "
            f"仅在 annotator_A 文件存在的 sample_id: {len(only_a)} 条；"
            f"示例: {only_a[:10]}"
        )
    if only_b:
        print(
            "[WARNING] "
            f"仅在 annotator_B 文件存在的 sample_id: {len(only_b)} 条；"
            f"示例: {only_b[:10]}"
        )


def _load_and_prepare(csv_path: Path, side_name: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    _validate_columns(df, csv_path)
    _warn_duplicates(df, side_name)

    prepared = (
        df[["sample_id", "annotator", "label"]]
        .rename(columns={"annotator": f"annotator_{side_name}", "label": f"label_{side_name}"})
        .drop_duplicates(subset=["sample_id"], keep="first")
    )
    return prepared


def build_disagreement_report(file_a: Path, file_b: Path) -> pd.DataFrame:
    a_df = _load_and_prepare(file_a, "A")
    b_df = _load_and_prepare(file_b, "B")

    aligned = a_df.merge(b_df, how="outer", on="sample_id")
    _warn_missing_ids(aligned)

    aligned["disagreement"] = aligned["label_A"] != aligned["label_B"]
    aligned["disagreement"] = aligned["disagreement"].fillna(True)

    aligned["label_pair"] = (
        aligned["label_A"].fillna("MISSING").astype(str)
        + "|"
        + aligned["label_B"].fillna("MISSING").astype(str)
    )

    output_df = aligned[
        ["sample_id", "annotator_A", "annotator_B", "disagreement", "label_pair"]
    ].sort_values(by="sample_id")
    return output_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="对齐两份标注 CSV，并输出分歧分析 CSV（MVP）。"
    )
    parser.add_argument("input_a", type=Path, help="第一份标注 CSV 路径")
    parser.add_argument("input_b", type=Path, help="第二份标注 CSV 路径")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("reports/day35_disagreement_analysis.csv"),
        help="输出 CSV 路径（默认: reports/day35_disagreement_analysis.csv）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_df = build_disagreement_report(args.input_a, args.input_b)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(args.output, index=False)

    total = len(report_df)
    mismatch = int(report_df["disagreement"].sum())
    print(f"对齐完成，总样本: {total}，disagreement: {mismatch}")
    print(f"输出文件: {args.output}")


if __name__ == "__main__":
    main()
