#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

import nltk
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from nltk.translate.meteor_score import meteor_score
from rouge_score.rouge_scorer import RougeScorer


class _NoWordNet:
    def synsets(self, _word: str) -> list[object]:
        return []


DEMO_SAMPLES = [
    {
        "sample_id": "exact_1",
        "experiment_type": "exact_match",
        "reference": "The cat sits on the warm mat",
        "candidate": "The cat sits on the warm mat",
    },
    {
        "sample_id": "syn_1",
        "experiment_type": "synonym_paraphrase",
        "reference": "The boy is very happy today",
        "candidate": "The child is very joyful today",
    },
    {
        "sample_id": "morph_1",
        "experiment_type": "stemming_morphology",
        "reference": "The runner runs quickly in the park",
        "candidate": "The runner running quickly in the park",
    },
    {
        "sample_id": "verbose_1",
        "experiment_type": "redundancy_verbose_output",
        "reference": "The project passed all tests",
        "candidate": "The project passed all tests with extra repeated details and many unnecessary words",
    },
    {
        "sample_id": "syn_2",
        "experiment_type": "synonym_paraphrase",
        "reference": "He solved the difficult problem fast",
        "candidate": "He fixed the hard issue quickly",
    },
]


def simple_tokenize(text: str) -> list[str]:
    return text.lower().split()


def compute_rows(samples: list[dict[str, str]]) -> list[dict[str, str | float]]:
    rouge = RougeScorer(["rougeL"], use_stemmer=True)
    smoothing = SmoothingFunction().method1
    rows: list[dict[str, str | float]] = []

    for sample in samples:
        reference_tokens = simple_tokenize(sample["reference"])
        candidate_tokens = simple_tokenize(sample["candidate"])

        try:
            meteor = float(meteor_score([reference_tokens], candidate_tokens))
        except LookupError:
            meteor = float(meteor_score([reference_tokens], candidate_tokens, wordnet=_NoWordNet()))
        bleu = float(
            sentence_bleu(
                [reference_tokens],
                candidate_tokens,
                smoothing_function=smoothing,
            )
        )
        rouge_l = float(rouge.score(sample["reference"], sample["candidate"])["rougeL"].fmeasure)

        print(
            "|".join(
                [
                    "INFO",
                    f"sample_id={sample['sample_id']}",
                    f"meteor={meteor:.6f}",
                    f"bleu={bleu:.6f}",
                    f"rougeL={rouge_l:.6f}",
                ]
            )
        )

        rows.append(
            {
                "sample_id": sample["sample_id"],
                "experiment_type": sample["experiment_type"],
                "meteor": meteor,
                "bleu": bleu,
                "rougeL": rouge_l,
                "reference": sample["reference"],
                "candidate": sample["candidate"],
            }
        )

    return rows


def save_csv(rows: list[dict[str, str | float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sample_id",
        "experiment_type",
        "meteor",
        "bleu",
        "rougeL",
        "reference",
        "candidate",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    nltk.download("wordnet")
    nltk.download("omw-1.4")

    rows = compute_rows(DEMO_SAMPLES)
    output_path = Path("outputs/day39_meteor_scores.csv")
    save_csv(rows, output_path)
    print(f"INFO|saved_csv={output_path}")


if __name__ == "__main__":
    main()
