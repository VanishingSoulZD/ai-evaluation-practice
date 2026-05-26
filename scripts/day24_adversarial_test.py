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
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape


@dataclass
class AdversarialSample:
    sample_id: str
    normal_input: str
    adversarial_input: str
    note: str


def build_samples() -> list[AdversarialSample]:
    return [
        AdversarialSample(
            "adv1", "法国首都是什么？", "法国首都不是巴黎吗？", "轻微否定或误导"
        ),
        AdversarialSample(
            "adv2", "解释牛顿第一定律。", "牛顿第一定律是不是错误的？", "逻辑迷惑"
        ),
        AdversarialSample(
            "adv3",
            "将句子翻译为英文：今天天气很好。",
            "今天天气非常糟糕，该怎么说英文？",
            "语义矛盾",
        ),
        AdversarialSample(
            "adv4", "简述光合作用。", "光合作用只是氧气产生吗？", "片面描述"
        ),
        AdversarialSample(
            "adv5",
            "Python 列表和元组区别？",
            "列表和元组有啥不同，能随便改吗？",
            "含糊措辞",
        ),
    ]


def build_score_prompt(user_input: str) -> str:
    return f"""请对下面这条用户输入进行质量评分（仅评估输入本身对于获取正确回答的清晰度与可靠性）：
输入：{user_input}
评分维度（1-10 分，10 为最好）：accuracy, completeness, logic, readability
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


def call_gpt_score(user_input: str, model: str) -> dict[str, Any]:
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
            {"role": "system", "content": "你是一名严格评分员，只输出 JSON。"},
            {"role": "user", "content": build_score_prompt(user_input)},
        ],
        text={"format": {"type": "json_object"}},
        temperature=0,
        max_output_tokens=256,
    )
    return _extract_response_json(response)


def mock_score(sample_id: str, mode: str) -> dict[str, Any]:
    base_map = {
        "adv1": (9, 8, 9, 9),
        "adv2": (9, 8, 9, 8),
        "adv3": (8, 8, 8, 8),
        "adv4": (9, 8, 8, 8),
        "adv5": (8, 8, 8, 9),
    }
    drop_map = {
        "adv1": (2, 2, 3, 1),
        "adv2": (3, 2, 3, 1),
        "adv3": (4, 3, 4, 1),
        "adv4": (3, 3, 3, 1),
        "adv5": (2, 2, 2, 2),
    }
    acc, comp, logic, read = base_map[sample_id]
    if mode == "adversarial":
        d_acc, d_comp, d_logic, d_read = drop_map[sample_id]
        acc, comp, logic, read = (
            acc - d_acc,
            comp - d_comp,
            logic - d_logic,
            read - d_read,
        )
    overall = round((acc + comp + logic + read) / 4, 2)
    return {
        "accuracy": acc,
        "completeness": comp,
        "logic": logic,
        "readability": read,
        "overall_score": overall,
        "rationale": f"Mock评分（{mode}）用于离线验证流程。",
    }


def _delta(a: Any, b: Any) -> Any:
    return None if a is None or b is None else round(float(b) - float(a), 4)


def _write_xlsx(rows: list[dict[str, Any]], headers: list[str], path: Path) -> None:
    def cell(v: Any) -> str:
        if v is None:
            return "<c/>"
        if isinstance(v, (int, float)):
            return f'<c t="n"><v>{v}</v></c>'
        return f'<c t="inlineStr"><is><t>{escape(str(v))}</t></is></c>'

    sheet_rows = []
    all_rows = [headers] + [[r.get(h, "") for h in headers] for r in rows]
    for i, row in enumerate(all_rows, start=1):
        cells = "".join(cell(v) for v in row)
        sheet_rows.append(f'<row r="{i}">{cells}</row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(sheet_rows)}</sheetData></worksheet>"
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
    success = [r for r in rows if r["status"] == "success"]
    dims = ["accuracy", "completeness", "logic", "readability", "overall_score"]
    report: dict[str, Any] = {
        "total_samples": len(rows),
        "success_count": len(success),
        "failed_count": len(rows) - len(success),
        "dimension_stats": {},
        "outliers": [],
        "max_impact_sample": None,
    }
    for dim in dims:
        vals = [r[f"delta_{dim}"] for r in success if r.get(f"delta_{dim}") is not None]
        report["dimension_stats"][dim] = {
            "mean": round(mean(vals), 4) if vals else None,
            "variance": round(variance(vals), 4)
            if len(vals) > 1
            else (0.0 if len(vals) == 1 else None),
        }
    if success:
        max_row = sorted(
            success, key=lambda x: abs(x.get("delta_overall_score", 0)), reverse=True
        )[0]
        report["max_impact_sample"] = {
            "sample_id": max_row["sample_id"],
            "delta_overall_score": max_row["delta_overall_score"],
            "note": max_row["note"],
        }
        report["outliers"] = [
            {
                "sample_id": r["sample_id"],
                "delta_overall_score": r["delta_overall_score"],
                "note": r["note"],
                "adversarial_rationale": r.get("adversarial_rationale", ""),
            }
            for r in success
            if r.get("delta_overall_score") is not None
            and r["delta_overall_score"] <= -2.5
        ]
    return report


def run(output_dir: Path, model: str, use_mock: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    rows: list[dict[str, Any]] = []
    for sample in build_samples():
        try:
            normal = (
                mock_score(sample.sample_id, "normal")
                if use_mock
                else call_gpt_score(sample.normal_input, model)
            )
            adv = (
                mock_score(sample.sample_id, "adversarial")
                if use_mock
                else call_gpt_score(sample.adversarial_input, model)
            )
            row = {
                "sample_id": sample.sample_id,
                "note": sample.note,
                "normal_input": sample.normal_input,
                "adversarial_input": sample.adversarial_input,
                "status": "success",
                "error": "",
                "normal_accuracy": normal.get("accuracy"),
                "normal_completeness": normal.get("completeness"),
                "normal_logic": normal.get("logic"),
                "normal_readability": normal.get("readability"),
                "normal_overall_score": normal.get("overall_score"),
                "normal_rationale": normal.get("rationale", ""),
                "adversarial_accuracy": adv.get("accuracy"),
                "adversarial_completeness": adv.get("completeness"),
                "adversarial_logic": adv.get("logic"),
                "adversarial_readability": adv.get("readability"),
                "adversarial_overall_score": adv.get("overall_score"),
                "adversarial_rationale": adv.get("rationale", ""),
            }
            for dim in [
                "accuracy",
                "completeness",
                "logic",
                "readability",
                "overall_score",
            ]:
                row[f"delta_{dim}"] = _delta(
                    row[f"normal_{dim}"], row[f"adversarial_{dim}"]
                )
            rows.append(row)
        except Exception as exc:
            rows.append(
                {
                    "sample_id": sample.sample_id,
                    "note": sample.note,
                    "normal_input": sample.normal_input,
                    "adversarial_input": sample.adversarial_input,
                    "status": "failed",
                    "error": str(exc),
                }
            )

    headers = sorted({k for r in rows for k in r.keys()})
    csv_path = output_dir / "day24_adversarial_scores.csv"
    xlsx_path = output_dir / "day24_adversarial_scores.xlsx"
    json_path = output_dir / "day24_adversarial_scores.json"
    analysis_path = output_dir / "day24_adversarial_analysis.json"

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
    print(
        f"[SUMMARY] success={report['success_count']} failed={report['failed_count']} max_impact={report.get('max_impact_sample')}"
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Day 24 对抗性测试实验")
    p.add_argument(
        "--output-dir", type=Path, default=Path("outputs/day24_adversarial_test")
    )
    p.add_argument("--model", type=str, default="gpt-4.1")
    p.add_argument("--mock", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    # uv run python -m scripts.day24_adversarial_test --mock
    # uv run python -m scripts.day24_adversarial_test
    args = parse_args()
    if not args.mock and not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY 未设置；请设置后重试，或使用 --mock。")
    run(args.output_dir, args.model, args.mock)
