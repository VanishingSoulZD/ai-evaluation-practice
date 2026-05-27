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
        "focus_tag": "control",
        "notes": "Control case with perfect surface overlap.",
        "reference": "The cat sits on the warm mat",
        "candidate": "The cat sits on the warm mat",
    },
    {
        "sample_id": "exact_2",
        "experiment_type": "exact_match",
        "focus_tag": "control",
        "notes": "Another control sample to stabilize exact-match average.",
        "reference": "She reads a book every night",
        "candidate": "She reads a book every night",
    },
    {
        "sample_id": "stem_1",
        "experiment_type": "stemming_effect",
        "focus_tag": "stemming",
        "notes": "Run/running morphology with minimal lexical change.",
        "reference": "The runner runs quickly in the park",
        "candidate": "The runner running quickly in the park",
    },
    {
        "sample_id": "stem_2",
        "experiment_type": "stemming_effect",
        "focus_tag": "stemming",
        "notes": "Solve/solving morphology to test stem tolerance.",
        "reference": "They solve difficult puzzles at school",
        "candidate": "They solving difficult puzzles at school",
    },
    {
        "sample_id": "stem_3",
        "experiment_type": "stemming_effect",
        "focus_tag": "stemming",
        "notes": "Analyze/analyzed morphology while keeping content intact.",
        "reference": "Scientists analyze the data carefully",
        "candidate": "Scientists analyzed the data carefully",
    },
    {
        "sample_id": "syn_1",
        "experiment_type": "synonym_match",
        "focus_tag": "synonym",
        "notes": "Boy/child and happy/joyful synonym replacement.",
        "reference": "The boy is very happy today",
        "candidate": "The child is very joyful today",
    },
    {
        "sample_id": "syn_2",
        "experiment_type": "synonym_match",
        "focus_tag": "synonym",
        "notes": "Difficult/hard and problem/issue synonym replacement.",
        "reference": "He solved the difficult problem fast",
        "candidate": "He solved the hard issue fast",
    },
    {
        "sample_id": "syn_3",
        "experiment_type": "synonym_match",
        "focus_tag": "synonym",
        "notes": "Small synonym paraphrase with preserved sentence structure.",
        "reference": "The movie was funny and exciting",
        "candidate": "The film was amusing and thrilling",
    },
    {
        "sample_id": "surface_1",
        "experiment_type": "surface_mismatch",
        "focus_tag": "surface",
        "notes": "Semantic closeness with lower direct lexical overlap.",
        "reference": "The team completed the project before the deadline",
        "candidate": "The group finished the assignment ahead of schedule",
    },
    {
        "sample_id": "surface_2",
        "experiment_type": "surface_mismatch",
        "focus_tag": "surface",
        "notes": "Paraphrase with multiple substitutions and phrase shifts.",
        "reference": "Please keep the room clean and quiet",
        "candidate": "Kindly maintain silence and cleanliness in this area",
    },
    {
        "sample_id": "order_1",
        "experiment_type": "order_or_noise",
        "focus_tag": "order",
        "notes": "Word-order perturbation with mostly identical tokens.",
        "reference": "The teacher explained the lesson clearly",
        "candidate": "Clearly the lesson explained the teacher",
    },
    {
        "sample_id": "noise_1",
        "experiment_type": "order_or_noise",
        "focus_tag": "noise",
        "notes": "Adds redundant tail to show precision sensitivity.",
        "reference": "The project passed all tests",
        "candidate": "The project passed all tests with extra repeated details and many unnecessary words",
    },
]


def simple_tokenize(text: str) -> list[str]:
    return text.lower().split()


def _trend_label(meteor: float, bleu: float, rouge_l: float) -> str:
    if meteor > bleu and meteor > rouge_l:
        return "meteor>bleu,rougeL"
    if meteor > bleu:
        return "meteor>bleu"
    if meteor > rouge_l:
        return "meteor>rougeL"
    return "meteor<=bleu,rougeL"


def compute_rows(samples: list[dict[str, str]]) -> list[dict[str, str | float]]:
    rouge = RougeScorer(["rougeL"], use_stemmer=True)
    smoothing = SmoothingFunction().method1
    rows: list[dict[str, str | float]] = []

    for sample in samples:
        reference_tokens = simple_tokenize(sample["reference"])
        candidate_tokens = simple_tokenize(sample["candidate"])

        try:
            meteor = float(meteor_score([reference_tokens], candidate_tokens))
            wordnet_used = "yes"
        except LookupError:
            meteor = float(meteor_score([reference_tokens], candidate_tokens, wordnet=_NoWordNet()))
            wordnet_used = "fallback_no_wordnet"
        bleu = float(
            sentence_bleu(
                [reference_tokens],
                candidate_tokens,
                smoothing_function=smoothing,
            )
        )
        rouge_l = float(rouge.score(sample["reference"], sample["candidate"])["rougeL"].fmeasure)
        trend = _trend_label(meteor, bleu, rouge_l)

        print(
            "|".join(
                [
                    "INFO",
                    f"sample_id={sample['sample_id']}",
                    f"experiment_type={sample['experiment_type']}",
                    f"focus_tag={sample['focus_tag']}",
                    f"meteor={meteor:.6f}",
                    f"bleu={bleu:.6f}",
                    f"rougeL={rouge_l:.6f}",
                    f"trend={trend}",
                    f"wordnet={wordnet_used}",
                ]
            )
        )

        rows.append(
            {
                "sample_id": sample["sample_id"],
                "experiment_type": sample["experiment_type"],
                "focus_tag": sample["focus_tag"],
                "notes": sample["notes"],
                "meteor": meteor,
                "bleu": bleu,
                "rougeL": rouge_l,
                "reference": sample["reference"],
                "candidate": sample["candidate"],
            }
        )

    return rows


def print_summary(rows: list[dict[str, str | float]]) -> None:
    summary: dict[str, dict[str, float]] = {}

    for row in rows:
        key = str(row["experiment_type"])
        if key not in summary:
            summary[key] = {"n": 0.0, "meteor": 0.0, "bleu": 0.0, "rougeL": 0.0}
        summary[key]["n"] += 1
        summary[key]["meteor"] += float(row["meteor"])
        summary[key]["bleu"] += float(row["bleu"])
        summary[key]["rougeL"] += float(row["rougeL"])

    for experiment_type, stats in summary.items():
        n = int(stats["n"])
        print(
            "|".join(
                [
                    "SUMMARY",
                    f"type={experiment_type}",
                    f"n={n}",
                    f"meteor_avg={stats['meteor'] / n:.6f}",
                    f"bleu_avg={stats['bleu'] / n:.6f}",
                    f"rougeL_avg={stats['rougeL'] / n:.6f}",
                ]
            )
        )


def save_csv(rows: list[dict[str, str | float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sample_id",
        "experiment_type",
        "focus_tag",
        "notes",
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
    print_summary(rows)
    output_path = Path("outputs/day39_meteor_scores.csv")
    save_csv(rows, output_path)
    print(f"INFO|saved_csv={output_path}")


if __name__ == "__main__":
    main()
