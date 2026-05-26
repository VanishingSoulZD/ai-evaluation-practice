#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, variance
from typing import Any
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


@dataclass
class DialogueSample:
    sample_id: str
    normal_input: str
    scene_note: str
    expected_keywords: list[str]


def build_samples() -> list[DialogueSample]:
    return [
        DialogueSample(
            "sim1",
            "北京是中国的首都吗？",
            "事实问答，回答应明确结论。",
            ["北京", "首都"],
        ),
        DialogueSample(
            "sim2",
            "请用三步说明如何煮鸡蛋。",
            "步骤型任务，强调结构化和完整性。",
            ["步骤", "水", "鸡蛋", "煮"],
        ),
        DialogueSample(
            "sim3",
            "总结：运动有助于健康，但要循序渐进。",
            "总结型任务，需覆盖利弊与建议。",
            ["运动", "健康", "循序渐进"],
        ),
        DialogueSample(
            "sim4",
            "用户说：我昨晚没睡好，今天很焦虑。你怎么安慰他？",
            "情感支持场景，要求同理心和建议。",
            ["理解", "休息", "建议", "专业帮助"],
        ),
        DialogueSample(
            "sim5",
            "比较列表(list)和元组(tuple)的区别。",
            "技术解释场景，强调准确性。",
            ["可变", "不可变", "list", "tuple"],
        ),
    ]


def build_chat_prompt(user_input: str, note: str) -> str:
    return f"你是一个对话助手，请根据用户输入给出自然、简洁、逻辑清晰的回答。\n场景说明：{note}\n用户输入：{user_input}"


def build_score_prompt(user_input: str, model_output: str) -> str:
    return f"""请对下面这条对话回复进行评分（1-10分，10为最好）：
用户输入：{user_input}
模型回答：{model_output}
评分维度：accuracy, completeness, logic, readability
请严格返回 JSON：
{{"accuracy": int, "completeness": int, "logic": int, "readability": int, "overall_score": float, "rationale": "..."}}"""


def _extract_response_json(response: Any) -> dict[str, Any]:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return json.loads(output_text)
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", "") == "output_text":
                return json.loads(getattr(content, "text", ""))
    raise ValueError("响应中无可解析 JSON")


def call_llm_answer(user_input: str, note: str, model: str) -> str:
    from openai import OpenAI

    # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    client = OpenAI(
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENROUTER_BASE_URL"),
    )
    model = "google/gemini-3.1-flash-lite-preview"
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "你是友好且可靠的中文助手。"},
            {"role": "user", "content": build_chat_prompt(user_input, note)},
        ],
        text={"format": {"type": "text"}},
        temperature=0,
        max_output_tokens=256,
    )
    output_text = getattr(response, "output_text", "")
    if not isinstance(output_text, str) or not output_text.strip():
        raise ValueError("模型未返回有效文本")
    return output_text.strip()


def call_llm_score(user_input: str, model_output: str, model: str) -> dict[str, Any]:
    from openai import OpenAI

    # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    client = OpenAI(
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENROUTER_BASE_URL"),
    )
    model = "google/gemini-3.1-flash-lite-preview"
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "你是一名严格评分员，只输出 JSON。"},
            {"role": "user", "content": build_score_prompt(user_input, model_output)},
        ],
        text={"format": {"type": "json_object"}},
        temperature=0,
        max_output_tokens=256,
    )
    return _extract_response_json(response)


def _bounded(n: float, min_v: int = 1, max_v: int = 10) -> int:
    return int(max(min_v, min(max_v, round(n))))


def mock_answer(sample: DialogueSample) -> str:
    answers = {
        "sim1": "是的，北京是中国的首都，也是政治文化中心。",
        "sim2": "可以分三步：1) 锅中加水并放入鸡蛋；2) 水开后中火煮8-10分钟；3) 捞出后过冷水更易剥壳。",
        "sim3": "运动能提升心肺功能和情绪状态，但应根据体能逐步增加强度，避免受伤。",
        "sim4": "我理解你今天很难受，先给自己一点缓冲时间，做几次深呼吸并尽量补休；若焦虑持续，建议联系专业人士。",
        "sim5": "list 和 tuple 都可存多个元素；list 可变，tuple 不可变，因此 tuple 更适合固定数据。",
    }
    return answers[sample.sample_id]


def mock_score(sample: DialogueSample, output: str) -> dict[str, Any]:
    text = output.lower()
    hit_count = sum(1 for k in sample.expected_keywords if k.lower() in text)
    completeness = _bounded(5 + hit_count)
    accuracy = _bounded(6 + (1 if hit_count >= 2 else 0))
    logic = (
        _bounded(7)
        if any(x in output for x in ["因此", "所以", "1)", "2)", "3)"])
        else _bounded(6)
    )
    readability = _bounded(8 if len(output) <= 120 else 6)
    overall = round((accuracy + completeness + logic + readability) / 4, 2)
    return {
        "accuracy": accuracy,
        "completeness": completeness,
        "logic": logic,
        "readability": readability,
        "overall_score": overall,
        "rationale": f"Mock评分：命中关键词 {hit_count}/{len(sample.expected_keywords)}",
    }


def _delta(value: Any, baseline: float = 7.0) -> float | None:
    return None if value is None else round(float(value) - baseline, 4)


def _write_xlsx(rows: list[dict[str, Any]], headers: list[str], path: Path) -> None:
    def cell(v: Any) -> str:
        if v is None:
            return "<c/>"
        if isinstance(v, (int, float)):
            return f'<c t="n"><v>{v}</v></c>'
        return f'<c t="inlineStr"><is><t>{escape(str(v))}</t></is></c>'

    all_rows = [headers] + [[r.get(h, "") for h in headers] for r in rows]
    sheet_rows = [
        f'<row r="{i}">{"".join(cell(v) for v in row)}</row>'
        for i, row in enumerate(all_rows, start=1)
    ]
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
        + "".join(sheet_rows)
        + "</sheetData></worksheet>"
    )
    workbook = '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="scores" sheetId="1" r:id="rId1"/></sheets></workbook>'
    rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    wb_rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
    content_types = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'
    with ZipFile(path, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    dims = ["accuracy", "completeness", "logic", "readability", "overall_score"]
    success_rows = [r for r in rows if r["status"] == "success"]
    report: dict[str, Any] = {
        "total_samples": len(rows),
        "success_count": len(success_rows),
        "failed_count": len(rows) - len(success_rows),
        "dimension_stats": {},
        "outlier_dialogues": [],
        "max_impact_sample": None,
    }
    for dim in dims:
        values = [float(r[dim]) for r in success_rows if r.get(dim) is not None]
        report["dimension_stats"][dim] = {
            "mean": round(mean(values), 4) if values else None,
            "variance": round(variance(values), 4)
            if len(values) > 1
            else (0.0 if len(values) == 1 else None),
        }
    report["outlier_dialogues"] = [
        {
            "sample_id": r["sample_id"],
            "overall_score": r["overall_score"],
            "delta_overall_score": r["delta_overall_score"],
            "rationale": r.get("rationale", ""),
        }
        for r in success_rows
        if r.get("overall_score") is not None and float(r["overall_score"]) < 5
    ]
    if success_rows:
        max_row = sorted(
            success_rows,
            key=lambda x: abs(float(x.get("delta_overall_score", 0))),
            reverse=True,
        )[0]
        report["max_impact_sample"] = {
            "sample_id": max_row["sample_id"],
            "delta_overall_score": max_row.get("delta_overall_score"),
            "overall_score": max_row.get("overall_score"),
            "scene_note": max_row.get("scene_note"),
        }
    return report


def run(output_dir: Path, model: str, use_mock: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    rows: list[dict[str, Any]] = []
    for sample in build_samples():
        try:
            response = (
                mock_answer(sample)
                if use_mock
                else call_llm_answer(sample.normal_input, sample.scene_note, model)
            )
            score = (
                mock_score(sample, response)
                if use_mock
                else call_llm_score(sample.normal_input, response, model)
            )
            row = {
                "sample_id": sample.sample_id,
                "normal_input": sample.normal_input,
                "scene_note": sample.scene_note,
                "model_output": response,
                "status": "success",
                "error": "",
                "accuracy": score.get("accuracy"),
                "completeness": score.get("completeness"),
                "logic": score.get("logic"),
                "readability": score.get("readability"),
                "overall_score": score.get("overall_score"),
                "rationale": score.get("rationale", ""),
            }
            for dim in [
                "accuracy",
                "completeness",
                "logic",
                "readability",
                "overall_score",
            ]:
                row[f"delta_{dim}"] = _delta(row[dim])
            rows.append(row)
        except Exception as exc:
            rows.append(
                {
                    "sample_id": sample.sample_id,
                    "normal_input": sample.normal_input,
                    "scene_note": sample.scene_note,
                    "model_output": "",
                    "status": "failed",
                    "error": str(exc),
                    "accuracy": None,
                    "completeness": None,
                    "logic": None,
                    "readability": None,
                    "overall_score": None,
                    "rationale": "",
                    "delta_accuracy": None,
                    "delta_completeness": None,
                    "delta_logic": None,
                    "delta_readability": None,
                    "delta_overall_score": None,
                }
            )

    headers = sorted({k for row in rows for k in row.keys()})
    csv_path = output_dir / "day25_simulation_scores.csv"
    xlsx_path = output_dir / "day25_simulation_scores.xlsx"
    json_path = output_dir / "day25_simulation_scores.json"
    analysis_path = output_dir / "day25_analysis_report.json"

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    _write_xlsx(rows, headers, xlsx_path)
    json_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = analyze(rows)
    analysis_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[OK] csv: {csv_path}")
    print(f"[OK] xlsx: {xlsx_path}")
    print(f"[OK] json: {json_path}")
    print(f"[OK] analysis: {analysis_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 25 仿真环境对话评估")
    parser.add_argument("--model", type=str, default="gpt-4.1")
    parser.add_argument("--mock", action="store_true", help="使用 Mock 对话与评分")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("outputs/day25_simulation_test")
    )
    return parser.parse_args()


if __name__ == "__main__":
    # uv run python -m scripts.day25_simulation_eval --mock
    # uv run python -m scripts.day25_simulation_eval
    args = parse_args()
    if not args.mock and not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY 未设置；请设置后重试，或使用 --mock。")
    run(args.output_dir, args.model, args.mock)
