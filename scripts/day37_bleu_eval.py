#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import csv
from statistics import mean

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


def generate_markdown_report(rows: list[dict[str, str | float]], output_path: Path) -> None:
    grouped: dict[str, list[dict[str, str | float]]] = {}
    for row in rows:
        exp_type = str(row["experiment_type"])
        grouped.setdefault(exp_type, []).append(row)

    def fmt_samples(exp_type: str) -> str:
        items: list[str] = []
        for row in grouped.get(exp_type, []):
            items.append(
                "- "
                f"`{row['sample_id']}` BLEU={float(row['bleu']):.6f} | "
                f"ref: \"{row['reference']}\" | cand: \"{row['candidate']}\""
            )
        return "\n".join(items) if items else "- (no sample)"

    def avg_bleu(exp_type: str) -> float:
        scores = [float(row["bleu"]) for row in grouped.get(exp_type, [])]
        return mean(scores) if scores else 0.0

    report = f"""# Day 37 BLEU Analysis Report

## 1. Introduction

This report explains **why BLEU changes** across experiments rather than only listing scores.
In this setup, BLEU is computed at sentence level using tokenized lowercased text (`split()`), so the metric focuses on **surface-form overlap** between candidate and reference.

BLEU is a classic **precision-oriented** metric: it emphasizes how much of the generated candidate can be matched by the reference.
It is less about whether the candidate fully covers all reference information.

---

## 2. BLEU Core Mechanisms

### 2.1 Precision-oriented

BLEU rewards candidate tokens and phrases that appear in the reference.
This means:
- generating unsupported words is penalized;
- conservative overlap is rewarded;
- but full content coverage is not directly optimized like a recall metric.

### 2.2 n-gram overlap

BLEU combines overlap across:
- **unigram (1-gram)**: word-level matching
- **bigram (2-gram)**: short phrase/order matching
- **trigram (3-gram)**: stronger local structure matching
- **4-gram**: strict phrase continuity and word-order consistency

Higher-order n-grams are much more sensitive to word order.
So two sentences with similar words can still get lower BLEU if phrase order changes.

### 2.3 Brevity penalty

BLEU includes a brevity penalty to prevent systems from outputting only short keyword fragments.
Even if a short candidate contains some correct words, it loses score because:
- many higher-order n-grams are absent;
- candidate length is too short compared with reference.

---

## 3. Experiment Analysis

### 3.1 exact_match

Average BLEU: **{avg_bleu("exact_match"):.6f}**

{fmt_samples("exact_match")}

Interpretation:
- Candidate and reference are identical, so overlap is perfect at all n-gram orders.
- This is the easiest case for BLEU and approaches the practical upper bound.
- It shows BLEU strongly rewards literal agreement in wording and order.

### 3.2 word_order_change

Average BLEU: **{avg_bleu("word_order_change"):.6f}**

{fmt_samples("word_order_change")}

Interpretation:
- Most words are preserved, so unigram overlap remains relatively strong.
- However, reordered phrasing breaks many bigram/trigram/4-gram matches.
- This causes a visible drop and demonstrates BLEU's sensitivity to local word order.

### 3.3 synonym_paraphrase

Average BLEU: **{avg_bleu("synonym_paraphrase"):.6f}**

{fmt_samples("synonym_paraphrase")}

Interpretation:
- Semantic meaning is similar, but lexical forms differ ("movie/film", "good/great", etc.).
- Because BLEU relies on exact token overlap, synonym substitutions can sharply reduce score.
- This demonstrates that BLEU does not directly capture semantic equivalence.

### 3.4 brevity_penalty

Average BLEU: **{avg_bleu("brevity_penalty"):.6f}**

{fmt_samples("brevity_penalty")}

Interpretation:
- Candidates keep only fragments of the reference.
- Short outputs lose score both from missing higher-order n-grams and brevity penalty.
- This shows BLEU discourages keyword-only outputs and favors sufficiently complete responses.

---

## 4. BLEU Limitations

1. **Semantic blindness**  
   BLEU matches surface forms, not deep meaning; semantically correct paraphrases may be undervalued.

2. **Paraphrase sensitivity**  
   Legitimate rewording and reordering can reduce overlap even when human quality is acceptable.

3. **Sentence-level instability**  
   Sentence BLEU can fluctuate strongly for short or stylistically varied outputs; single-sentence interpretation should be cautious.

4. **Single-reference limitation**  
   One reference cannot cover all valid phrasings, so BLEU may penalize alternative correct expressions.

---

## 5. Conclusion

BLEU is a foundational **overlap-based** metric that is useful for monitoring textual agreement with references.
However, BLEU is not equivalent to true semantic quality.
It is most reliable in tasks where phrasing is relatively constrained.

For robust evaluation, BLEU should be combined with:
- **ROUGE** (overlap from another angle),
- **BERTScore** (semantic similarity),
- **LLM Judge** (instruction-following and coherence),
- **human evaluation** (final quality grounding).
"""
    output_path.write_text(report, encoding="utf-8")


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

    md_output_path = output_dir / "day37_bleu_analysis.md"
    generate_markdown_report(rows, md_output_path)

    print(f"INFO|csv_saved={output_path}")
    print(f"INFO|markdown_saved={md_output_path}")
    print("INFO|day37_bleu_eval_done")


if __name__ == "__main__":
    # uv run python -m scripts.day37_bleu_eval
    main()
