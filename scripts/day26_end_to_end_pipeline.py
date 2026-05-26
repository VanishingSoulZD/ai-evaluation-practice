#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, variance
from typing import Any
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


@dataclass
class Sample:
    sample_id: str
    user_input: str
    reference_output: str
    scene_note: str
    expected_keywords: list[str]


def build_samples() -> list[Sample]:
    """覆盖 Week1~Week4 多场景：事实、步骤、总结、情感支持、技术解释、风险判断。"""
    return [
        Sample(
            "w1_fact_01",
            "地球围绕太阳公转吗？",
            "是的，地球围绕太阳公转，周期约 365 天。",
            "事实问答",
            ["是", "地球", "太阳", "365"],
        ),
        Sample(
            "w1_steps_02",
            "请用三步说明如何进行番茄炒蛋。",
            "1) 处理食材；2) 先炒蛋后炒番茄；3) 合炒并调味出锅。",
            "步骤说明",
            ["1", "2", "3", "先", "后", "调味"],
        ),
        Sample(
            "w2_summary_03",
            "总结：远程办公提高灵活性，但沟通成本上升。",
            "远程办公提升灵活性与效率，但需通过制度和工具降低沟通成本。",
            "总结型任务",
            ["灵活", "沟通", "成本", "制度", "工具"],
        ),
        Sample(
            "w2_emotion_04",
            "我最近一直失眠，白天很崩溃。",
            "先表达理解并给出可执行建议，必要时建议求助专业医生。",
            "情感支持",
            ["理解", "建议", "作息", "专业", "医生"],
        ),
        Sample(
            "w3_tech_05",
            "解释 HTTP 和 HTTPS 的主要区别。",
            "HTTPS = HTTP + TLS/SSL，具备加密、认证与完整性保护。",
            "技术解释",
            ["TLS", "加密", "认证", "完整性"],
        ),
        Sample(
            "w3_compare_06",
            "比较 Python 列表和集合。",
            "列表有序可重复；集合无序去重，适合成员检测。",
            "对比解释",
            ["有序", "可重复", "无序", "去重"],
        ),
        Sample(
            "w4_risk_07",
            "有人让我把短信验证码发给他，这安全吗？",
            "不安全，验证码属于敏感信息，不应分享。",
            "安全风险判断",
            ["不安全", "敏感", "不要", "验证码"],
        ),
        Sample(
            "w4_reason_08",
            "为什么要做代码评审？",
            "代码评审可提升质量、发现缺陷、促进知识共享并降低维护风险。",
            "逻辑解释",
            ["质量", "缺陷", "共享", "风险"],
        ),
    ]


def mock_model_output(sample: Sample) -> str:
    outputs = {
        "w1_fact_01": "是的，地球绕太阳公转一周大约是365天。",
        "w1_steps_02": "三步：1) 切番茄打蛋；2) 先炒蛋盛出，再炒番茄；3) 回锅混合并调味。",
        "w2_summary_03": "远程办公更灵活，但沟通和协作成本会上升，需要配套机制。",
        "w2_emotion_04": "听起来你真的很辛苦。可以先固定作息、减少咖啡因，若持续失眠建议就医。",
        "w3_tech_05": "HTTPS 在 HTTP 基础上增加 TLS，加密传输并提供身份认证与完整性保护。",
        "w3_compare_06": "列表通常可保持顺序且可重复；集合无序且自动去重，查成员更快。",
        "w4_risk_07": "这不安全，短信验证码不要给任何人。",
        "w4_reason_08": "代码评审能提前发现问题，统一风格，并促进团队知识流动。",
    }
    return outputs[sample.sample_id]


def bounded(v: float, lo: int = 1, hi: int = 10) -> int:
    return int(max(lo, min(hi, round(v))))


def score_sample(sample: Sample, model_output: str) -> dict[str, Any]:
    text = model_output.lower()
    hits = sum(1 for k in sample.expected_keywords if k.lower() in text)
    completeness = bounded(4 + hits)
    accuracy = bounded(6 + (1 if hits >= len(sample.expected_keywords) // 2 else 0))
    logic = bounded(
        7
        if any(
            x in model_output for x in ["因为", "所以", "1)", "2)", "3)", "先", "再"]
        )
        else 6
    )
    readability = bounded(8 if len(model_output) <= 120 else 6)
    overall = round((accuracy + completeness + logic + readability) / 4, 2)
    return {
        "accuracy": accuracy,
        "completeness": completeness,
        "logic": logic,
        "readability": readability,
        "overall_score": overall,
        "rationale": f"命中关键词 {hits}/{len(sample.expected_keywords)}",
    }


def delta(v: float, baseline: float = 7.0) -> float:
    return round(v - baseline, 4)


def detect_outliers(rows: list[dict[str, Any]]) -> list[str]:
    vals = [float(r["overall_score"]) for r in rows]
    m = mean(vals)
    var = variance(vals) if len(vals) > 1 else 0.0
    std = var**0.5
    if std == 0:
        return []
    low, high = m - std, m + std
    return [
        r["sample_id"]
        for r in rows
        if float(r["overall_score"]) < low or float(r["overall_score"]) > high
    ]


def write_xlsx(
    rows: list[dict[str, Any]], headers: list[str], path: Path, sheet_name: str
) -> None:
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
    workbook = f'<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="{escape(sheet_name)}" sheetId="1" r:id="rId1"/></sheets></workbook>'
    rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    wb_rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
    content_types = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'
    with ZipFile(path, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def run(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    samples = build_samples()

    annotation_rows = [
        {
            "sample_id": s.sample_id,
            "input": s.user_input,
            "reference_output": s.reference_output,
            "scene_note": s.scene_note,
        }
        for s in samples
    ]

    metrics_rows: list[dict[str, Any]] = []
    for s in samples:
        model_output = mock_model_output(s)
        metric = score_sample(s, model_output)
        row = {
            "sample_id": s.sample_id,
            "input": s.user_input,
            "reference_output": s.reference_output,
            "scene_note": s.scene_note,
            "model_output": model_output,
            **metric,
        }
        row["delta_overall_score"] = delta(float(row["overall_score"]))
        metrics_rows.append(row)

    outliers = detect_outliers(metrics_rows)
    for r in metrics_rows:
        r["is_outlier"] = r["sample_id"] in outliers

    dims = ["accuracy", "completeness", "logic", "readability", "overall_score"]
    dimension_stats = {}
    for d in dims:
        vals = [float(r[d]) for r in metrics_rows]
        dimension_stats[d] = {
            "mean": round(mean(vals), 4),
            "variance": round(variance(vals), 4) if len(vals) > 1 else 0.0,
        }

    success_count = sum(1 for r in metrics_rows if float(r["overall_score"]) >= 7)
    failed_count = len(metrics_rows) - success_count
    max_impact = max(metrics_rows, key=lambda r: abs(float(r["delta_overall_score"])))

    analysis_report = {
        "total_samples": len(metrics_rows),
        "success_count": success_count,
        "failed_count": failed_count,
        "dimension_stats": dimension_stats,
        "outlier_samples": [
            {
                "sample_id": r["sample_id"],
                "overall_score": r["overall_score"],
                "delta_overall_score": r["delta_overall_score"],
                "scene_note": r["scene_note"],
                "rationale": r["rationale"],
            }
            for r in metrics_rows
            if r["is_outlier"]
        ],
        "max_impact_sample": {
            "sample_id": max_impact["sample_id"],
            "overall_score": max_impact["overall_score"],
            "delta_overall_score": max_impact["delta_overall_score"],
            "scene_note": max_impact["scene_note"],
        },
    }

    (output_dir / "day26_annotation.json").write_text(
        json.dumps(annotation_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "day26_metrics.json").write_text(
        json.dumps(metrics_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (output_dir / "day26_metrics.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        headers = list(metrics_rows[0].keys())
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(metrics_rows)
    write_xlsx(
        metrics_rows,
        list(metrics_rows[0].keys()),
        output_dir / "day26_metrics.xlsx",
        "day26_metrics",
    )
    (output_dir / "day26_analysis_report.json").write_text(
        json.dumps(analysis_report, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    # uv run python -m scripts.day26_end_to_end_pipeline
    parser = argparse.ArgumentParser(description="Day26 标注→指标→报告全流程")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/day26_end_to_end_pipeline"),
        help="输出目录",
    )
    args = parser.parse_args()
    run(args.output_dir)
    print(f"[OK] 输出目录: {args.output_dir}")
