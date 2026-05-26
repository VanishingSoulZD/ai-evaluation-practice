#!/usr/bin/env python3
"""Day 23: 使用 GPT 进行小规模 LLM 自动评分实验。"""

from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, variance
from typing import Any

import pandas as pd


@dataclass
class Sample:
    """实验样本，包含问题、参考答案与被测答案。"""

    sample_id: str
    question: str
    reference: str
    prediction: str


def build_samples() -> list[Sample]:
    """构造内置小规模样本集（8 条）。"""
    return [
        Sample("s1", "法国首都是什么？", "巴黎", "法国首都是巴黎。"),
        Sample(
            "s2",
            "解释牛顿第一定律。",
            "物体在不受外力时保持静止或匀速直线运动。",
            "牛顿第一定律说没有外力时物体状态不变。",
        ),
        Sample(
            "s3",
            "将句子翻译为英文：今天天气很好。",
            "The weather is very nice today.",
            "Today weather very good.",
        ),
        Sample(
            "s4",
            "简述光合作用。",
            "植物利用光能把二氧化碳和水转化为有机物并释放氧气。",
            "植物靠阳光制造养分并释放氧气。",
        ),
        Sample(
            "s5",
            "什么是二分查找？",
            "在有序数组中通过不断折半定位目标的搜索算法。",
            "二分查找就是从中间开始比较并缩小范围。",
        ),
        Sample("s6", "列举两种可再生能源。", "太阳能、风能。", "煤炭和石油。"),
        Sample(
            "s7",
            "总结：AI 可提升效率但有偏见风险。",
            "AI 能提升生产效率，但需控制偏见与伦理风险。",
            "AI 有好处也有风险。",
        ),
        Sample(
            "s8",
            "Python 中列表和元组的区别？",
            "列表可变，元组不可变。",
            "列表和元组都能存多个值，但元组通常不可改。",
        ),
    ]


def build_prompt(sample: Sample) -> str:
    """构造评分 Prompt，要求模型返回结构化 JSON。"""
    return f"""
请根据以下维度对回答进行评分（1-10）：
1) 准确性 2) 完整性 3) 逻辑性 4) 可读性

问题：{sample.question}
参考答案：{sample.reference}
被测答案：{sample.prediction}

请严格返回 JSON：
{{
  "accuracy": int,
  "completeness": int,
  "logic": int,
  "readability": int,
  "overall_score": float,
  "rationale": "..."
}}
""".strip()


def _extract_response_json(response: Any) -> dict[str, Any]:
    """优先解析 output_text，不可用时回退解析 output 中的 JSON 片段。"""
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return json.loads(output_text)

    output = getattr(response, "output", None)
    if not isinstance(output, list):
        raise ValueError("responses.create 返回结果缺少可解析的 output")

    for item in output:
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", "") == "output_text":
                text = getattr(content, "text", "")
                if isinstance(text, str) and text.strip():
                    return json.loads(text)
            if getattr(content, "type", "") == "json_schema":
                parsed = getattr(content, "parsed", None)
                if isinstance(parsed, dict):
                    return parsed
    raise ValueError("未在 response.output 中找到可解析 JSON")


def call_gpt_score(sample: Sample, model: str) -> dict[str, Any]:
    """调用 OpenAI Responses API 获取评分结果。"""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    # client = OpenAI(
    #     api_key=os.environ.get("OPENROUTER_API_KEY"),
    #     base_url=os.environ.get("OPENROUTER_BASE_URL"),
    # )
    # model = "google/gemini-3.1-flash-lite-preview"
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "你是一名严格的文本评分员，只返回 JSON。"},
            {"role": "user", "content": build_prompt(sample)},
        ],
        text={"format": {"type": "json_object"}},
        temperature=0,
        max_output_tokens=256,
    )
    return _extract_response_json(response)


def mock_score(sample: Sample) -> dict[str, Any]:
    """无 API 时使用的本地 Mock，便于流程演示。"""
    bad = "煤炭" in sample.prediction or "石油" in sample.prediction
    base = 3 if bad else 8
    return {
        "accuracy": base,
        "completeness": max(1, base - 1),
        "logic": base,
        "readability": min(10, base + 1),
        "overall_score": round(
            (base + max(1, base - 1) + base + min(10, base + 1)) / 4, 2
        ),
        "rationale": "Mock 评分：用于离线验证流程。",
    }


def analyze_scores(df: pd.DataFrame) -> dict[str, Any]:
    """对评分结果计算均值、方差并检查异常值（总体分 < 5）。"""
    dims = ["accuracy", "completeness", "logic", "readability", "overall_score"]
    success_df = df[df["status"] == "success"].copy()
    stats: dict[str, Any] = {
        "success_count": int(len(success_df)),
        "failed_count": int(len(df) - len(success_df)),
    }
    for dim in dims:
        values = success_df[dim].dropna().tolist()
        if not values:
            stats[dim] = {"mean": None, "variance": None}
            continue
        stats[dim] = {
            "mean": round(mean(values), 4),
            "variance": round(variance(values), 4) if len(values) > 1 else 0.0,
        }
    outliers = success_df[success_df["overall_score"] < 5][
        ["sample_id", "overall_score", "rationale"]
    ]
    stats["outliers"] = outliers.to_dict(orient="records")
    return stats


def run(output_dir: Path, model: str, use_mock: bool) -> None:
    """执行评分、落盘结果并输出分析报告。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("day23_llm_judge")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    samples = build_samples()
    rows: list[dict[str, Any]] = []

    for sample in samples:
        try:
            score = (
                mock_score(sample) if use_mock else call_gpt_score(sample, model=model)
            )
            rows.append(
                {
                    "sample_id": sample.sample_id,
                    "question": sample.question,
                    "reference": sample.reference,
                    "prediction": sample.prediction,
                    "status": "success",
                    "error": "",
                    **score,
                }
            )
            logger.info("sample_id=%s 评分成功", sample.sample_id)
        except Exception as exc:
            logger.exception("sample_id=%s 评分失败: %s", sample.sample_id, exc)
            rows.append(
                {
                    "sample_id": sample.sample_id,
                    "question": sample.question,
                    "reference": sample.reference,
                    "prediction": sample.prediction,
                    "status": "failed",
                    "error": str(exc),
                    "accuracy": None,
                    "completeness": None,
                    "logic": None,
                    "readability": None,
                    "overall_score": None,
                    "rationale": "",
                }
            )

    df = pd.DataFrame(rows)
    csv_path = output_dir / "day23_scores.csv"
    xlsx_path = output_dir / "day23_scores.xlsx"
    json_path = output_dir / "day23_scores.json"
    analysis_path = output_dir / "day23_analysis.json"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    analysis = analyze_scores(df)
    analysis_path.write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[OK] scores csv: {csv_path}")
    print(f"[OK] scores xlsx: {xlsx_path}")
    print(f"[OK] scores json: {json_path}")
    print(f"[OK] analysis: {analysis_path}")
    print("[INFO] outlier count:", len(analysis.get("outliers", [])))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 23 LLM 自动评分实验")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("outputs/day23_llm_judge")
    )
    parser.add_argument("--model", type=str, default="gpt-4.1")
    parser.add_argument(
        "--mock", action="store_true", help="使用本地 mock 评分，跳过真实 API"
    )
    return parser.parse_args()


if __name__ == "__main__":
    # uv run python -m scripts.day23_llm_judge_experiment --mock
    # uv run python -m scripts.day23_llm_judge_experiment
    args = parse_args()
    if not args.mock and not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY 未设置；请设置后重试，或使用 --mock。")
    run(output_dir=args.output_dir, model=args.model, use_mock=args.mock)
