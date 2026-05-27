#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import csv

from nltk.translate.bleu_score import sentence_bleu


DEMO_SAMPLES = [
    {
        "sample_id": "s1_exact_match",
        "reference": "The cat is on the mat",
        "candidate": "The cat is on the mat",
    },
    {
        "sample_id": "s2_word_order_changed",
        "reference": "The cat is on the mat",
        "candidate": "On the mat the cat is",
    },
    {
        "sample_id": "s3_paraphrase_synonym",
        "reference": "The movie was very good",
        "candidate": "The film was really great",
    },
    {
        "sample_id": "s4_very_short_output",
        "reference": "The weather is warm and sunny today",
        "candidate": "warm",
    },
]


def simple_tokenize(text: str) -> list[str]:
    return text.lower().split()


def compute_sentence_bleu(reference: str, candidate: str) -> float:
    reference_tokens = simple_tokenize(reference)
    candidate_tokens = simple_tokenize(candidate)
    return sentence_bleu([reference_tokens], candidate_tokens)


def main() -> None:
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "day37_bleu_scores.csv"

    rows: list[dict[str, str | float]] = []

    print("INFO|day37_bleu_eval_start")
    for sample in DEMO_SAMPLES:
        bleu = compute_sentence_bleu(sample["reference"], sample["candidate"])
        print(
            f"BLEU|sample_id={sample['sample_id']}|bleu={bleu:.6f}|"
            f"reference={sample['reference']}|candidate={sample['candidate']}"
        )
        rows.append(
            {
                "sample_id": sample["sample_id"],
                "bleu": round(bleu, 6),
                "reference": sample["reference"],
                "candidate": sample["candidate"],
            }
        )

    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["sample_id", "bleu", "reference", "candidate"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"INFO|csv_saved={output_path}")
    print("INFO|day37_bleu_eval_done")


if __name__ == "__main__":
    # uv run python -m scripts.day37_bleu_eval
    main()
