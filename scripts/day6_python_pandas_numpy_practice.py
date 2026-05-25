#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 6 教学版脚本：
Python 基础复习 + Pandas / NumPy 数据处理练习

这个脚本的设计目标不是只完成统计结果，而是把 Day 6 任务里要求的能力完整串起来：
1. Python 基础语法与数据结构
2. Pandas 的读取、筛选、排序、groupby、merge、apply/map
3. NumPy 的数组、切片、广播、聚合
4. 基于小数据集做可复现的数据分析输出

你可以把它当成一个“边跑边学”的示例脚本。
"""

from __future__ import annotations
# 使用未来注解特性，让类型标注更稳定，减少运行时求值带来的问题。

import argparse
# argparse 用于解析命令行参数，方便从终端传入输入文件、输出目录和列名配置。

import json
# json 用于把 Python 对象保存成 JSON 文件，适合保存教学示例中的结构化结果。

import re
# re 用于正则表达式匹配，这里用于从标注文本中识别实体标签和情感标签。

from datetime import datetime
# datetime 用于生成时间戳，保证每次输出文件名唯一，便于对比多次运行结果。

from pathlib import Path
# Path 用于安全、清晰地处理文件路径，避免字符串拼接路径带来的错误。

import numpy as np
# NumPy 用于数组、切片、广播、聚合等数值计算，是 Day 6 的重点练习内容之一。

import pandas as pd
# Pandas 用于表格数据读取、清洗、筛选、分组、合并和导出，是本脚本的核心依赖。


# 预定义实体标签类型。
# 这样做的好处是：
# 1. 后续提取标签时有统一标准；
# 2. 如果 Day 5/Day 6 的标注格式扩展，只需要在这里调整；
# 3. 便于输出统计结果时保持列名一致。
ENTITY_TYPES = ["PER", "ORG", "LOC", "TIME"]


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数。

    教学目标：
    - 学会用 argparse 构造一个可复用的脚本入口
    - 理解“位置参数”和“可选参数”的区别
    - 理解如何通过参数适配不同数据表结构
    """
    parser = argparse.ArgumentParser(
        description="Day6: Python 基础复习与 Pandas/NumPy 数据处理练习"
    )

    # 位置参数：必须传入，表示输入文件路径。
    # 支持 CSV 或 Excel 文件。
    parser.add_argument(
        "input_file",
        type=Path,
        help="Day5/历史标注数据 CSV 或 Excel",
    )

    # 可选参数：输出目录。
    # 默认值放在 reports/day6_practice，便于统一管理训练结果。
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/day6_practice"),
        help="输出目录",
    )

    # 下面几个参数是为了适配不同数据源中的列名。
    # 因为真实项目里，列名经常不是完全固定的。
    parser.add_argument("--id-col", default="ID")
    parser.add_argument("--task-col", default="任务类型")
    parser.add_argument("--text-col", default="原始文本")
    parser.add_argument("--label-col", default="标注结果")

    return parser.parse_args()


def load_table(path: Path) -> pd.DataFrame:
    """
    根据文件后缀自动加载 CSV 或 Excel。

    教学目标：
    - 学会处理不同格式数据源
    - 理解 read_csv / read_excel 的差异
    - 掌握简单的文件类型分发逻辑
    """
    suffix = path.suffix.lower()

    # CSV 是最常见的轻量表格格式。
    # utf-8-sig 可以兼容带 BOM 的 CSV 文件，避免中文首列出现异常字符。
    if suffix == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig")

    # Excel 通常用于人工整理后的练习数据。
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)

    # 如果输入不是支持的格式，就直接报错，避免脚本静默失败。
    raise ValueError("仅支持 CSV/XLSX 文件")


def python_basics_demo() -> dict[str, object]:
    """
    Python 基础语法与数据结构演示。

    教学目标：
    - 列表、集合、字典
    - 字符串清洗
    - 循环与条件判断
    - 函数定义与默认参数
    - 推导式写法

    这一部分不依赖外部数据，目的是把“Python 基础能力”单独练一遍。
    """
    # 创建一个列表，里面刻意包含重复值。
    # 这样后面可以演示去重、排序和推导式。
    numbers = [1, 2, 2, 3, 5, 8]

    # set 会自动去重。
    # sorted 会把结果排序，得到稳定、可读的输出。
    unique_sorted = sorted(set(numbers))

    # 列表推导式：对每个数字求平方。
    squares = [n * n for n in unique_sorted]

    # 字典推导式：构建“数字 -> 平方”的映射。
    num_map = {n: n * n for n in unique_sorted}

    # 字符串原始值，前后带空格，便于演示 strip / lower / replace。
    sentence = "  Python Data Processing Day6  "

    # strip 去掉首尾空白，lower 统一小写，replace 把空格替换为下划线。
    normalized = sentence.strip().lower().replace(" ", "_")

    # 统计元音字母数量。
    # 这里 sum 的参数是布尔值序列，True 会当成 1，False 会当成 0。
    vowel_count = sum(ch in "aeiou" for ch in normalized)

    # 用一个循环统计偶数之和。
    # 这用于演示 for + if 的基础控制流。
    total = 0
    for value in unique_sorted:
        if value % 2 == 0:
            total += value

    # 定义一个局部函数，演示函数参数和默认值。
    def scale(x: int, factor: int = 10) -> int:
        return x * factor

    # 返回一个字典，便于后续写入 JSON。
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
    """
    从标注结果文本中提取实体类型标签。

    教学目标：
    - 练习正则表达式
    - 学会从复杂文本中抽取结构化信息
    - 为后续 groupby / explode 统计做准备

    例如：
    - "PER: 张三, ORG: 百度"
    - "LOC: 重庆, TIME: 2024年"
    """
    # 如果不是字符串，说明这一行可能缺失、格式异常，或者是空值。
    # 直接返回空列表，避免正则报错。
    if not isinstance(label_text, str):
        return []

    tags: list[str] = []

    # 遍历预定义实体类型。
    for entity_type in ENTITY_TYPES:
        # 这个正则表示：
        # - 前面是单词边界 \b
        # - 匹配 PER / ORG / LOC / TIME
        # - 后面允许跟任意空格再接冒号
        # 这样可以兼容 "PER:" 和 "PER :" 两种写法。
        if re.search(rf"\b{entity_type}\s*:", label_text):
            tags.append(entity_type)

    return tags


def build_pandas_outputs(
    df: pd.DataFrame,
    id_col: str,
    task_col: str,
    text_col: str,
    label_col: str,
) -> dict[str, pd.DataFrame]:
    """
    进行 Pandas 数据处理并输出多个统计表。

    教学目标：
    - 数据清洗
    - 列创建
    - apply / map / str.contains / str.extract
    - groupby 分组统计
    - explode 展开列表
    - merge 合并结果
    - duplicated 检查重复

    这一部分对应 Day 6 的核心练习目标。
    """
    # 为避免直接修改原始输入，先复制一份。
    data = df.copy()

    # 检查关键列是否存在。
    # 如果列缺失，创建空列占位，保证后续流程不中断。
    for col in [id_col, task_col, text_col, label_col]:
        if col not in data.columns:
            print(f"[WARN] 缺失列 {col}，将使用空列占位继续处理。")
            data[col] = ""

    # 把标签列中的空值填充为空字符串，再统一转为字符串。
    # 这样后面的正则处理、contains、extract 都更安全。
    data[label_col] = data[label_col].fillna("").astype(str)

    # 文本列也做同样处理，防止 len 或字符串操作报错。
    data[text_col] = data[text_col].fillna("").astype(str)

    # 先抓取所有连续的大写 token，用于检查是否出现未知标签。
    # 例如 POS、NEG、NEU、PER、ORG 等。
    raw_label_tokens = data[label_col].str.findall(r"\b[A-Z]{3,}\b")

    # 已知标签集合。
    # 这个集合是本脚本的“白名单”。
    known_tokens = {
        "POS",
        "NEG",
        "NEU",
        "PER",
        "ORG",
        "LOC",
        "TIME",
        "BIO",
        "B",
        "I",
        "O",
    }

    # 找出不在白名单中的 token。
    # 这是一个简单的数据质量检查步骤。
    unknown_tokens = sorted(
        {
            token
            for tokens in raw_label_tokens
            for token in tokens
            if token not in known_tokens
        }
    )

    # 如果发现异常标签，给出提示。
    if unknown_tokens:
        print(f"[WARN] 检测到未识别标签: {unknown_tokens}")

    # 生成文本长度特征。
    # map(len) 是非常常见的列级别转换用法。
    data["text_len"] = data[text_col].map(len)

    # 根据任务类型内容把样本粗分为“分类 / 实体 / 其他”。
    # apply + lambda 是很常见的列级映射方式。
    data["task_group"] = data[task_col].apply(
        lambda x: (
            "分类" if "分类" in str(x) else ("实体" if "实体" in str(x) else "其他")
        )
    )

    # 判断当前样本是否包含情感标签。
    # 返回的是布尔值列，便于后续求和统计。
    data["has_sentiment"] = data[label_col].str.contains(
        r"\b(?:POS|NEG|NEU)\b", regex=True
    )

    # 提取实体标签列表。
    # 每一行会得到一个 list，例如 ["PER", "ORG"]。
    data["entity_tags"] = data[label_col].apply(extract_entity_tags)

    # ---------------------------------------------------------
    # 1) groupby：按任务分组统计
    # ---------------------------------------------------------
    # groupby 是数据分析里最核心的操作之一。
    # 它的本质是“按某个维度分组，然后对每组做聚合”。
    task_stats = (
        data.groupby("task_group", as_index=False)
        .agg(
            # 每组样本数
            samples=(id_col, "count"),
            # 每组平均文本长度
            avg_text_len=("text_len", "mean"),
            # 每组中包含情感标签的行数
            sentiment_rows=("has_sentiment", "sum"),
        )
        # 按样本数排序，方便阅读
        .sort_values("samples", ascending=False)
    )

    # ---------------------------------------------------------
    # 2) explode + groupby：统计实体标签分布
    # ---------------------------------------------------------
    # explode 会把一行里的列表拆成多行。
    # 例如 entity_tags = ["PER", "ORG"] 的样本，会拆成两行。
    entity_exploded = data[[id_col, "entity_tags"]].explode("entity_tags")

    # 删除没有实体标签的空行。
    entity_exploded = entity_exploded.dropna(subset=["entity_tags"])

    # 按 entity_tags 分组计数，得到实体分布。
    entity_dist = (
        entity_exploded.groupby("entity_tags", as_index=False)
        .agg(count=(id_col, "count"))
        .rename(columns={"entity_tags": "entity_label"})
        .sort_values("count", ascending=False)
    )

    # ---------------------------------------------------------
    # 3) merge：演示数据合并
    # ---------------------------------------------------------
    # 这里用一个常量 key 做合并，是为了教学演示 merge 的使用方式。
    # 在真实业务里，一般会用真实业务键（如样本 ID、用户 ID、时间戳等）合并。
    task_stats["key"] = 1
    entity_dist["key"] = 1

    # outer 合并保留双方所有行。
    # 这样可以把两个统计表拼成一个“联合视图”。
    merged_view = pd.merge(task_stats, entity_dist, on="key", how="outer").drop(
        columns=["key"]
    )

    # ---------------------------------------------------------
    # 4) 分类标签分布统计
    # ---------------------------------------------------------
    # 从标注文本中提取 POS / NEG / NEU。
    # 没提取到的样本统一标记为 UNLABELED。
    label_counts = (
        data[label_col]
        .str.extract(r"\b(POS|NEG|NEU)\b", expand=False)
        .fillna("UNLABELED")
        .value_counts(dropna=False)
        .rename_axis("label")
        .reset_index(name="count")
    )

    # 计算占比。
    # max(len(data), 1) 是防止空表时除零。
    label_counts["ratio"] = label_counts["count"] / max(len(data), 1)

    # 输出未标注样本数量。
    unlabeled_count = int(
        label_counts.loc[label_counts["label"] == "UNLABELED", "count"].sum()
    )
    print(f"[INFO] 未标注样本数量(UNLABELED): {unlabeled_count}")

    # ---------------------------------------------------------
    # 5) 重复统计
    # ---------------------------------------------------------
    # duplicated(subset=[...]) 用来检查指定列的重复值。
    # 它返回的是布尔序列，True 表示这行是重复项。
    duplicate_stats = pd.DataFrame(
        [
            {"metric": "total_rows", "value": int(len(data))},
            {
                "metric": "duplicate_id_rows",
                "value": int(data.duplicated(subset=[id_col]).sum()),
            },
            {
                "metric": "duplicate_text_rows",
                "value": int(data.duplicated(subset=[text_col]).sum()),
            },
        ]
    )

    # 把所有结果集中返回，便于主函数统一导出。
    return {
        "cleaned_data": data,
        "task_stats": task_stats,
        "entity_distribution": entity_dist,
        "task_entity_merged": merged_view,
        "label_distribution": label_counts,
        "duplicate_stats": duplicate_stats,
    }


def build_numpy_outputs(df: pd.DataFrame) -> dict[str, object]:
    """
    对清洗后的数据做 NumPy 练习。

    教学目标：
    - DataFrame 列转 NumPy 数组
    - 数组切片
    - 广播运算
    - 聚合函数
    - 条件筛选
    - 标准化处理

    这里主要使用文本长度作为数值样本，因为它最容易理解。
    """
    # 将 text_len 列转成 NumPy 数组。
    # 指定 int64 是为了让数值类型更明确。
    text_len = df["text_len"].to_numpy(dtype=np.int64)

    # 创建与 text_len 同形状的全 1 数组。
    # 这样可以演示向量加法。
    ones = np.ones_like(text_len)

    # 广播运算：所有文本长度统一加 5。
    plus_five = text_len + 5

    # 计算标准差，用于后续做标准化。
    std_value = text_len.std()

    # 当标准差为 0 时，说明所有值都一样。
    # 此时如果直接除以 0 会报错，所以需要兜底。
    if std_value == 0:
        print("[WARN] text_len 标准差为 0，归一化将使用 1 作为分母。")

    # 标准化公式： (x - mean) / std
    # 这是数据处理里常见的数值变换。
    normalized = (text_len - text_len.mean()) / (std_value if std_value else 1)

    # 用中位数构造条件掩码，判断哪些文本属于“长文本”。
    long_text_mask = text_len >= np.median(text_len)

    return {
        # 数组形状，帮助理解数据的维度。
        "array_shape": list(text_len.shape),
        # 切片：前 5 个元素。
        "slice_first_5": text_len[:5].tolist(),
        # 广播运算结果：前 5 个元素加 5。
        "broadcast_plus_five_first_5": plus_five[:5].tolist(),
        # 满足“长文本”条件的样本数。
        "mask_long_text_count": int(long_text_mask.sum()),
        # 基本聚合统计。
        "aggregations": {
            "sum": int(np.sum(text_len)),
            "mean": float(np.mean(text_len)),
            "max": int(np.max(text_len)) if text_len.size else 0,
            "min": int(np.min(text_len)) if text_len.size else 0,
        },
        # 向量化相加演示：前 5 个元素加 1。
        "vector_add_demo_first_5": (text_len[:5] + ones[:5]).tolist(),
        # 标准化结果：前 5 个元素，保留 4 位小数。
        "normalized_first_5": np.round(normalized[:5], 4).tolist(),
    }


def main() -> None:
    """
    主入口函数。

    教学目标：
    - 理解脚本从“参数 -> 读表 -> 处理 -> 输出 -> 打印总结”的完整流程
    - 学会把多个独立练习函数串成一个可复现的数据处理脚本
    """
    # 解析命令行参数。
    args = parse_args()

    # 创建输出目录。
    # parents=True 表示上层目录不存在也一并创建。
    # exist_ok=True 表示目录已存在时不报错。
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # 读取输入表格。
    df = load_table(args.input_file)

    # 运行 Python 基础练习。
    basics = python_basics_demo()

    # 运行 Pandas 处理部分。
    pandas_outputs = build_pandas_outputs(
        df,
        args.id_col,
        args.task_col,
        args.text_col,
        args.label_col,
    )

    # 运行 NumPy 处理部分。
    numpy_outputs = build_numpy_outputs(pandas_outputs["cleaned_data"])

    # 为输出文件加时间戳，避免重名覆盖。
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 将所有 Pandas 表格逐个导出为 CSV。
    # 这里用循环是为了演示“批量输出多个结果文件”的做法。
    for name, table in pandas_outputs.items():
        table.to_csv(
            args.output_dir / f"{name}.csv",
            index=False,
            encoding="utf-8-sig",
        )

    # 保存 Python 基础练习结果。
    # ensure_ascii=False 可以正确写出中文。
    # indent=2 让 JSON 更容易阅读。
    (args.output_dir / "python_basics_demo.json").write_text(
        json.dumps(basics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 保存 NumPy 练习结果。
    (args.output_dir / "numpy_summary.json").write_text(
        json.dumps(numpy_outputs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 下面重新汇总几个最关键的指标，便于命令行查看。
    total_rows = int(len(pandas_outputs["cleaned_data"]))
    dup_id_rows = int(
        pandas_outputs["cleaned_data"].duplicated(subset=[args.id_col]).sum()
    )
    dup_text_rows = int(
        pandas_outputs["cleaned_data"].duplicated(subset=[args.text_col]).sum()
    )
    unlabeled_rows = int(
        pandas_outputs["label_distribution"]
        .loc[pandas_outputs["label_distribution"]["label"] == "UNLABELED", "count"]
        .sum()
    )

    # 打印运行结果摘要。
    # 这些信息可以帮助你快速判断脚本是否正确执行。
    print(f"[INFO] 样本总数: {total_rows}")
    print(f"[INFO] 重复 ID 数量: {dup_id_rows}")
    print(f"[INFO] 重复文本数量: {dup_text_rows}")
    print(f"[INFO] 未标注样本数量: {unlabeled_rows}")
    print(f"Day6 练习完成：输出目录 {args.output_dir}，文件时间戳 {timestamp}")


# 标准 Python 主入口写法。
# 只有当你直接执行这个文件时，main() 才会运行。
# 如果这个文件被别的模块 import，则不会自动触发主流程。
if __name__ == "__main__":
    # uv run python -m scripts.day6_python_pandas_numpy_practice data/day02_annotation.csv
    # uv run python -m scripts.day6_python_pandas_numpy_practice data/day02_annotation.xlsx
    main()
