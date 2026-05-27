#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import csv

from rouge_score import rouge_scorer


DEMO_SAMPLES = [
    {
        "sample_id": "exact_1",
        "experiment_type": "exact_match",
        "reference": "The cat sat on the mat and looked outside.",
        "candidate": "The cat sat on the mat and looked outside.",
    },
    {
        "sample_id": "missing_1",
        "experiment_type": "information_missing",
        "reference": "The report says quarterly revenue increased by 12 percent with strong growth in cloud services.",
        "candidate": "The report says revenue increased.",
    },
    {
        "sample_id": "syn_1",
        "experiment_type": "synonym_paraphrase",
        "reference": "The committee approved the proposal after a long discussion.",
        "candidate": "After an extended debate, the panel accepted the plan.",
    },
    {
        "sample_id": "stuff_1",
        "experiment_type": "keyword_stuffing",
        "reference": "The vaccine reduced severe cases in older adults.",
        "candidate": "vaccine severe older adults vaccine vaccine reduced severe cases adults older vaccine",
    },
    {
        "sample_id": "long_1",
        "experiment_type": "long_sequence",
        "reference": "In the final chapter, the author describes how small daily habits compound over years, and explains that consistency matters more than occasional bursts of motivation when building long-term skills.",
        "candidate": "The author explains in the final chapter that long-term skills come from consistency and small daily habits that compound over many years, not from occasional motivation bursts.",
    },
    {
        "sample_id": "long_2",
        "experiment_type": "long_sequence",
        "reference": "The engineering team migrated the service in three phases: database replication, read traffic shadowing, and final cutover, while monitoring latency and error rate at each stage.",
        "candidate": "The team migrated in phases including database replication and shadowing, then cut over while tracking latency and errors during each stage.",
    },
]


def build_demo_samples() -> list[dict[str, str]]:
    return DEMO_SAMPLES


def compute_rouge_scores(samples: list[dict[str, str]]) -> list[dict[str, str | float]]:
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    rows: list[dict[str, str | float]] = []

    for sample in samples:
        scores = scorer.score(sample["reference"], sample["candidate"])
        rouge1 = float(scores["rouge1"].fmeasure)
        rouge2 = float(scores["rouge2"].fmeasure)
        rougel = float(scores["rougeL"].fmeasure)

        print(
            "|".join(
                [
                    f"sample_id={sample['sample_id']}",
                    f"rouge1={rouge1:.6f}",
                    f"rouge2={rouge2:.6f}",
                    f"rougeL={rougel:.6f}",
                ]
            )
        )

        rows.append(
            {
                "sample_id": sample["sample_id"],
                "experiment_type": sample["experiment_type"],
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
    rows = compute_rouge_scores(samples)

    output_path = Path("outputs/day38_rouge_scores.csv")
    save_results(rows, output_path)

    print(f"INFO|saved_csv={output_path}")


if __name__ == "__main__":
    main()
