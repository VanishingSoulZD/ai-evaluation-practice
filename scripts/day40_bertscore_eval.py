#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

from bert_score import score


DEMO_SAMPLES = [
    {
        "sample_id": "exact_1",
        "case_type": "exact_match",
        "reference": "The cat is sleeping on the warm sofa.",
        "candidate": "The cat is sleeping on the warm sofa.",
    },
    {
        "sample_id": "syn_1",
        "case_type": "synonym_paraphrase",
        "reference": "The meeting was canceled because of heavy rain.",
        "candidate": "The conference was called off due to intense rainfall.",
    },
    {
        "sample_id": "rewrite_1",
        "case_type": "wording_rewrite",
        "reference": "The engineer fixed the production bug in one hour.",
        "candidate": "It took the developer about an hour to resolve the live issue.",
    },
    {
        "sample_id": "contradiction_1",
        "case_type": "semantic_contradiction",
        "reference": "The store opens at 9 AM every weekday.",
        "candidate": "The store never opens on weekdays and stays closed.",
    },
    {
        "sample_id": "partial_1",
        "case_type": "partial_overlap",
        "reference": "The report highlights strong growth in cloud revenue this quarter.",
        "candidate": "The report highlights growth in revenue.",
    },
    {
        "sample_id": "noise_1",
        "case_type": "extra_noise",
        "reference": "Please back up the database before the migration.",
        "candidate": "Please back up the database before the migration, and also print every page and sing loudly.",
    },
]


def compute_bertscore_rows(samples: list[dict[str, str]]) -> list[dict[str, str | float]]:
    references = [sample["reference"] for sample in samples]
    candidates = [sample["candidate"] for sample in samples]

    precision, recall, f1 = score(candidates, references, lang="en", verbose=False)

    rows: list[dict[str, str | float]] = []
    for idx, sample in enumerate(samples):
        p = float(precision[idx].item())
        r = float(recall[idx].item())
        f = float(f1[idx].item())

        print(
            "|".join(
                [
                    "INFO",
                    f"sample_id={sample['sample_id']}",
                    f"case_type={sample['case_type']}",
                    f"bertscore_precision={p:.6f}",
                    f"bertscore_recall={r:.6f}",
                    f"bertscore_f1={f:.6f}",
                ]
            )
        )

        rows.append(
            {
                "sample_id": sample["sample_id"],
                "bertscore_precision": p,
                "bertscore_recall": r,
                "bertscore_f1": f,
                "reference": sample["reference"],
                "candidate": sample["candidate"],
            }
        )

    return rows


def save_csv(rows: list[dict[str, str | float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sample_id",
        "bertscore_precision",
        "bertscore_recall",
        "bertscore_f1",
        "reference",
        "candidate",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = compute_bertscore_rows(DEMO_SAMPLES)
    output_path = Path("outputs/day40_bertscore_scores.csv")
    save_csv(rows, output_path)

    avg_f1 = sum(float(row["bertscore_f1"]) for row in rows) / len(rows)
    print(f"INFO|primary_metric=bertscore_f1|average={avg_f1:.6f}")
    print(f"INFO|saved_csv={output_path}|rows={len(rows)}")


if __name__ == "__main__":
    main()
