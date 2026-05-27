#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import csv

from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from rouge_score import rouge_scorer


DEMO_SAMPLES = [
    {
        "sample_id": "exact_1",
        "experiment_type": "exact_match",
        "lcs_case": "na",
        "notes": "Exact overlap baseline across all metrics.",
        "reference": "The cat sat on the mat and looked outside.",
        "candidate": "The cat sat on the mat and looked outside.",
    },
    {
        "sample_id": "missing_1",
        "experiment_type": "information_missing",
        "lcs_case": "na",
        "notes": "Coverage drop example with short candidate.",
        "reference": "The report says quarterly revenue increased by 12 percent with strong growth in cloud services.",
        "candidate": "The report says revenue increased.",
    },
    {
        "sample_id": "syn_1",
        "experiment_type": "synonym_paraphrase",
        "lcs_case": "na",
        "notes": "Semantic similarity with low lexical overlap.",
        "reference": "The committee approved the proposal after a long discussion.",
        "candidate": "After an extended debate, the panel accepted the plan.",
    },
    {
        "sample_id": "stuff_1",
        "experiment_type": "keyword_stuffing",
        "lcs_case": "na",
        "notes": "Keyword repetition to contrast BLEU/ROUGE behavior.",
        "reference": "The vaccine reduced severe cases in older adults.",
        "candidate": "vaccine severe older adults vaccine vaccine reduced severe cases adults older vaccine",
    },
    {
        "sample_id": "long_1",
        "experiment_type": "long_sequence",
        "lcs_case": "na",
        "notes": "Long sentence with mostly preserved structure.",
        "reference": "In the final chapter, the author describes how small daily habits compound over years, and explains that consistency matters more than occasional bursts of motivation when building long-term skills.",
        "candidate": "The author explains in the final chapter that long-term skills come from consistency and small daily habits that compound over many years, not from occasional motivation bursts.",
    },
    {
        "sample_id": "long_2",
        "experiment_type": "long_sequence",
        "lcs_case": "na",
        "notes": "Long sentence compression with partial phrase preservation.",
        "reference": "The engineering team migrated the service in three phases: database replication, read traffic shadowing, and final cutover, while monitoring latency and error rate at each stage.",
        "candidate": "The team migrated in phases including database replication and shadowing, then cut over while tracking latency and errors during each stage.",
    },
    {
        "sample_id": "lcs_1",
        "experiment_type": "rougeL_lcs_behavior",
        "lcs_case": "order_preserved",
        "notes": "Baseline for LCS: mostly same order and near-contiguous matching.",
        "reference": "The product team launched the beta program for enterprise customers last quarter.",
        "candidate": "The product team launched the beta program for enterprise customers last quarter.",
    },
    {
        "sample_id": "lcs_2",
        "experiment_type": "rougeL_lcs_behavior",
        "lcs_case": "gapped_match",
        "notes": "Keeps core token order but inserts noise words between matched tokens.",
        "reference": "The product team launched the beta program for enterprise customers last quarter.",
        "candidate": "The product team quickly launched the beta pilot program for enterprise premium customers last quarter.",
    },
    {
        "sample_id": "lcs_3",
        "experiment_type": "rougeL_lcs_behavior",
        "lcs_case": "local_reorder",
        "notes": "Swaps nearby phrases to hurt local bigram continuity.",
        "reference": "The product team launched the beta program for enterprise customers last quarter.",
        "candidate": "The product team for enterprise customers launched the beta program last quarter.",
    },
    {
        "sample_id": "lcs_4",
        "experiment_type": "rougeL_lcs_behavior",
        "lcs_case": "global_reorder",
        "notes": "Large-scale reorder preserves many words but disrupts overall sequence order.",
        "reference": "The product team launched the beta program for enterprise customers last quarter.",
        "candidate": "Last quarter, for enterprise customers, the beta program was launched by the product team.",
    },
]


def build_demo_samples() -> list[dict[str, str]]:
    return DEMO_SAMPLES


def _simple_tokenize(text: str) -> list[str]:
    return text.lower().split()


def _metric_pattern(rouge1: float, rouge2: float, rougel: float) -> str:
    if abs(rouge1 - rougel) <= 0.02 and rougel > rouge2:
        return "r1≈rL>r2"
    if rouge1 >= rougel >= rouge2:
        if rougel > rouge2:
            return "r1>=rL>r2"
        return "r1>=rL>=r2"
    if rouge1 >= rouge2 >= rougel:
        return "r1>=r2>=rL"
    return "mixed"


def compute_scores(samples: list[dict[str, str]]) -> list[dict[str, str | float]]:
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    smoothing = SmoothingFunction().method1
    rows: list[dict[str, str | float]] = []

    for sample in samples:
        reference_tokens = _simple_tokenize(sample["reference"])
        candidate_tokens = _simple_tokenize(sample["candidate"])
        bleu = float(sentence_bleu([reference_tokens], candidate_tokens, smoothing_function=smoothing))

        scores = scorer.score(sample["reference"], sample["candidate"])
        rouge1 = float(scores["rouge1"].fmeasure)
        rouge2 = float(scores["rouge2"].fmeasure)
        rougel = float(scores["rougeL"].fmeasure)
        pattern = _metric_pattern(rouge1, rouge2, rougel)

        print(
            "|".join(
                [
                    "INFO",
                    f"sample_id={sample['sample_id']}",
                    f"type={sample['experiment_type']}",
                    f"case={sample['lcs_case']}",
                    f"bleu={bleu:.6f}",
                    f"rouge1={rouge1:.6f}",
                    f"rouge2={rouge2:.6f}",
                    f"rougeL={rougel:.6f}",
                    f"pattern={pattern}",
                ]
            )
        )

        rows.append(
            {
                "sample_id": sample["sample_id"],
                "experiment_type": sample["experiment_type"],
                "lcs_case": sample["lcs_case"],
                "notes": sample["notes"],
                "bleu": bleu,
                "rouge1": rouge1,
                "rouge2": rouge2,
                "rougeL": rougel,
                "reference": sample["reference"],
                "candidate": sample["candidate"],
            }
        )

    return rows


def save_results(rows: list[dict[str, str | float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sample_id",
        "experiment_type",
        "lcs_case",
        "notes",
        "bleu",
        "rouge1",
        "rouge2",
        "rougeL",
        "reference",
        "candidate",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    samples = build_demo_samples()
    rows = compute_scores(samples)

    output_path = Path("outputs/day38_rouge_scores.csv")
    save_results(rows, output_path)

    print(f"INFO|saved_csv={output_path}")


if __name__ == "__main__":
    main()
