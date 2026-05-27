#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import csv

from nltk.translate.bleu_score import sentence_bleu


DEMO_SAMPLES = [
    {
        "sample_id": "exact_1",
        "experiment_type": "exact_match",
        "reference": "The cat is on the mat",
        "candidate": "The cat is on the mat",
        "explanation": "Perfect overlap at all n-gram orders, so BLEU is maximal.",
    },
    {
        "sample_id": "exact_2",
        "experiment_type": "exact_match",
        "reference": "Machine translation needs careful evaluation",
        "candidate": "Machine translation needs careful evaluation",
        "explanation": "Reference and candidate are identical.",
    },
    {
        "sample_id": "order_1",
        "experiment_type": "word_order_change",
        "reference": "The cat is on the mat",
        "candidate": "On the mat the cat is",
        "explanation": "Words are similar, but many higher-order n-grams are broken by word-order changes.",
    },
    {
        "sample_id": "order_2",
        "experiment_type": "word_order_change",
        "reference": "I really like this natural language processing course",
        "candidate": "This natural language processing course I really like",
        "explanation": "Semantic meaning is close, but BLEU penalizes reordered phrases.",
    },
    {
        "sample_id": "syn_1",
        "experiment_type": "synonym_paraphrase",
        "reference": "The movie was very good",
        "candidate": "The film was really great",
        "explanation": "Synonyms change surface forms, so n-gram overlap drops.",
    },
    {
        "sample_id": "syn_2",
        "experiment_type": "synonym_paraphrase",
        "reference": "He solved the problem quickly",
        "candidate": "He fixed the issue rapidly",
        "explanation": "Meaning is preserved, but BLEU stays low due to lexical mismatch.",
    },
    {
        "sample_id": "brevity_1",
        "experiment_type": "brevity_penalty",
        "reference": "The weather is warm and sunny today",
        "candidate": "warm",
        "explanation": "Very short output causes heavy brevity penalty and missing n-grams.",
    },
    {
        "sample_id": "brevity_2",
        "experiment_type": "brevity_penalty",
        "reference": "We need a detailed and complete project report",
        "candidate": "complete report",
        "explanation": "Candidate captures a fragment but is too short, so BLEU is strongly reduced.",
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
            f"BLEU|sample_id={sample['sample_id']}|experiment_type={sample['experiment_type']}|"
            f"bleu={bleu:.6f}|reference={sample['reference']}|candidate={sample['candidate']}"
        )
        print(f"EXPLAIN|sample_id={sample['sample_id']}|{sample['explanation']}")
        rows.append(
            {
                "sample_id": sample["sample_id"],
                "experiment_type": sample["experiment_type"],
                "bleu": round(bleu, 6),
                "reference": sample["reference"],
                "candidate": sample["candidate"],
                "explanation": sample["explanation"],
            }
        )

    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["sample_id", "experiment_type", "bleu", "reference", "candidate", "explanation"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"INFO|csv_saved={output_path}")
    print("INFO|day37_bleu_eval_done")


if __name__ == "__main__":
    # uv run python -m scripts.day37_bleu_eval
    main()
