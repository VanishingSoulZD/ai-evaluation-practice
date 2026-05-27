#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

from bert_score import score


DEMO_SAMPLES = [
    {"sample_id": "exact_1", "experiment_type": "exact_match", "expected_relation": "exact", "reference": "The cat is sleeping on the warm sofa.", "candidate": "The cat is sleeping on the warm sofa."},
    {"sample_id": "exact_2", "experiment_type": "exact_match", "expected_relation": "exact", "reference": "We launched the update this morning.", "candidate": "We launched the update this morning."},
    {"sample_id": "exact_3", "experiment_type": "exact_match", "expected_relation": "exact", "reference": "Please close the window before leaving.", "candidate": "Please close the window before leaving."},
    {"sample_id": "sem_1", "experiment_type": "semantic_similarity", "expected_relation": "synonym_paraphrase", "reference": "The boy is very happy with his results.", "candidate": "The child is delighted by his scores."},
    {"sample_id": "sem_2", "experiment_type": "semantic_similarity", "expected_relation": "synonym_paraphrase", "reference": "We need to start the deployment now.", "candidate": "It is time to begin the release immediately."},
    {"sample_id": "sem_3", "experiment_type": "semantic_similarity", "expected_relation": "synonym_paraphrase", "reference": "The meeting was canceled because of heavy rain.", "candidate": "The conference was called off due to intense rainfall."},
    {"sample_id": "para_1", "experiment_type": "paraphrase", "expected_relation": "paraphrase", "reference": "The committee approved the budget after a long discussion.", "candidate": "After debating for a long time, the panel gave the budget its approval."},
    {"sample_id": "para_2", "experiment_type": "paraphrase", "expected_relation": "paraphrase", "reference": "She finished the task before the deadline despite limited resources.", "candidate": "Even with scarce resources, she completed the work ahead of schedule."},
    {"sample_id": "para_3", "experiment_type": "paraphrase", "expected_relation": "paraphrase", "reference": "The product failed in tests, so the launch was delayed.", "candidate": "Because testing exposed defects, the release date was postponed."},
    {"sample_id": "word_1", "experiment_type": "wording_rewrite", "expected_relation": "wording_rewrite", "reference": "The engineer fixed the production bug in one hour.", "candidate": "It took the developer about an hour to resolve the live issue."},
    {"sample_id": "word_2", "experiment_type": "wording_rewrite", "expected_relation": "wording_rewrite", "reference": "Please back up the database before migration.", "candidate": "Kindly create a database backup prior to the migration process."},
    {"sample_id": "word_3", "experiment_type": "wording_rewrite", "expected_relation": "wording_rewrite", "reference": "Our team shipped the feature earlier than expected.", "candidate": "The feature was delivered by our group sooner than anticipated."},
    {"sample_id": "contra_1", "experiment_type": "semantic_contradiction", "expected_relation": "contradiction", "reference": "The store opens at 9 AM every weekday.", "candidate": "The store is closed all weekdays and never opens at 9 AM."},
    {"sample_id": "contra_2", "experiment_type": "semantic_contradiction", "expected_relation": "contradiction", "reference": "The patient improved after treatment.", "candidate": "The patient became much worse after treatment."},
    {"sample_id": "contra_3", "experiment_type": "semantic_contradiction", "expected_relation": "contradiction", "reference": "Revenue increased by twenty percent this quarter.", "candidate": "Revenue dropped by twenty percent this quarter."},
    {"sample_id": "contra_4", "experiment_type": "semantic_contradiction", "expected_relation": "contradiction", "reference": "The package arrived on Tuesday.", "candidate": "The package did not arrive on Tuesday."},
    {"sample_id": "partial_1", "experiment_type": "partial_overlap", "expected_relation": "partial", "reference": "The report highlights strong growth in cloud revenue this quarter.", "candidate": "The report highlights growth in revenue."},
    {"sample_id": "partial_2", "experiment_type": "partial_overlap", "expected_relation": "partial", "reference": "The model reduced latency by forty percent in production.", "candidate": "The model reduced latency."},
    {"sample_id": "partial_3", "experiment_type": "partial_overlap", "expected_relation": "partial", "reference": "Our roadmap includes security upgrades and audit automation.", "candidate": "The roadmap includes security upgrades."},
    {"sample_id": "noise_1", "experiment_type": "extra_noise", "expected_relation": "noisy_candidate", "reference": "Please back up the database before the migration.", "candidate": "Please back up the database before the migration, and also print every page and sing loudly."},
    {"sample_id": "noise_2", "experiment_type": "extra_noise", "expected_relation": "noisy_candidate", "reference": "Send me the final report by noon.", "candidate": "Send me the final report by noon, then dance in the hallway and recite random movie quotes for ten minutes."},
]


def tokenize(text: str) -> list[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text)
    return [t for t in cleaned.split() if t]


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def compute_bleu(candidate: str, reference: str) -> float:
    cand_tokens = tokenize(candidate)
    ref_tokens = tokenize(reference)
    if not cand_tokens:
        return 0.0
    precisions: list[float] = []
    for n in range(1, 5):
        cand_ngrams = ngrams(cand_tokens, n)
        ref_ngrams = ngrams(ref_tokens, n)
        if not cand_ngrams:
            precisions.append(0.0)
            continue
        ref_counts: dict[tuple[str, ...], int] = defaultdict(int)
        for ng in ref_ngrams:
            ref_counts[ng] += 1
        hit = 0
        for ng in cand_ngrams:
            if ref_counts[ng] > 0:
                hit += 1
                ref_counts[ng] -= 1
        precisions.append(safe_div(hit, len(cand_ngrams)))
    if min(precisions) == 0.0:
        geo_mean = 0.0
    else:
        geo_mean = math.exp(sum(math.log(p) for p in precisions) / 4.0)
    bp = 1.0 if len(cand_tokens) > len(ref_tokens) else math.exp(1 - safe_div(len(ref_tokens), len(cand_tokens)))
    return geo_mean * bp


def lcs_len(a: list[str], b: list[str]) -> int:
    dp = [0] * (len(b) + 1)
    for ta in a:
        prev = 0
        for j, tb in enumerate(b, start=1):
            cur = dp[j]
            if ta == tb:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = cur
    return dp[-1]


def compute_rouge(candidate: str, reference: str) -> tuple[float, float]:
    cand_tokens = tokenize(candidate)
    ref_tokens = tokenize(reference)
    if not cand_tokens or not ref_tokens:
        return 0.0, 0.0

    overlap = 0
    ref_counts: dict[str, int] = defaultdict(int)
    for t in ref_tokens:
        ref_counts[t] += 1
    for t in cand_tokens:
        if ref_counts[t] > 0:
            overlap += 1
            ref_counts[t] -= 1

    p1 = safe_div(overlap, len(cand_tokens))
    r1 = safe_div(overlap, len(ref_tokens))
    rouge1_f = safe_div(2 * p1 * r1, p1 + r1) if p1 + r1 else 0.0

    lcs = lcs_len(cand_tokens, ref_tokens)
    pl = safe_div(lcs, len(cand_tokens))
    rl = safe_div(lcs, len(ref_tokens))
    rouge_l_f = safe_div(2 * pl * rl, pl + rl) if pl + rl else 0.0
    return rouge1_f, rouge_l_f


def compute_meteor(candidate: str, reference: str) -> float:
    cand_tokens = tokenize(candidate)
    ref_tokens = tokenize(reference)
    if not cand_tokens or not ref_tokens:
        return 0.0
    overlap = 0
    ref_counts: dict[str, int] = defaultdict(int)
    for t in ref_tokens:
        ref_counts[t] += 1
    for t in cand_tokens:
        if ref_counts[t] > 0:
            overlap += 1
            ref_counts[t] -= 1
    precision = safe_div(overlap, len(cand_tokens))
    recall = safe_div(overlap, len(ref_tokens))
    if precision == 0.0 or recall == 0.0:
        return 0.0
    return (10 * precision * recall) / (recall + 9 * precision)


def compute_rows(samples: list[dict[str, str]]) -> list[dict[str, str | float]]:
    references = [s["reference"] for s in samples]
    candidates = [s["candidate"] for s in samples]
    b_p, b_r, b_f1 = score(candidates, references, lang="en", verbose=False)

    rows: list[dict[str, str | float]] = []
    for idx, sample in enumerate(samples):
        bleu = compute_bleu(sample["candidate"], sample["reference"])
        rouge1_f, rouge_l_f = compute_rouge(sample["candidate"], sample["reference"])
        meteor = compute_meteor(sample["candidate"], sample["reference"])
        p = float(b_p[idx].item())
        r = float(b_r[idx].item())
        f1 = float(b_f1[idx].item())

        print(
            "|".join([
                "INFO",
                f"sample_id={sample['sample_id']}",
                f"type={sample['experiment_type']}",
                f"bleu={bleu:.6f}",
                f"meteor={meteor:.6f}",
                f"bertscore_f1={f1:.6f}",
            ])
        )

        rows.append({
            "sample_id": sample["sample_id"],
            "experiment_type": sample["experiment_type"],
            "expected_relation": sample["expected_relation"],
            "reference": sample["reference"],
            "candidate": sample["candidate"],
            "bleu": bleu,
            "rouge1_f": rouge1_f,
            "rougeL_f": rouge_l_f,
            "meteor": meteor,
            "bertscore_precision": p,
            "bertscore_recall": r,
            "bertscore_f1": f1,
        })
    return rows


def print_group_summary(rows: list[dict[str, str | float]]) -> None:
    grouped: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["experiment_type"])].append(row)

    for group in sorted(grouped):
        part = grouped[group]
        n = len(part)
        avg_bleu = sum(float(r["bleu"]) for r in part) / n
        avg_rouge = sum(float(r["rouge1_f"]) for r in part) / n
        avg_meteor = sum(float(r["meteor"]) for r in part) / n
        avg_bs = sum(float(r["bertscore_f1"]) for r in part) / n
        print(
            "|".join([
                "INFO",
                "group_avg",
                f"experiment_type={group}",
                f"count={n}",
                f"bleu={avg_bleu:.6f}",
                f"rouge1_f={avg_rouge:.6f}",
                f"meteor={avg_meteor:.6f}",
                f"bertscore_f1={avg_bs:.6f}",
            ])
        )

        if group in {"semantic_similarity", "paraphrase", "wording_rewrite"}:
            print(f"INFO|insight=bertscore_advantage|group={group}|delta_vs_bleu={(avg_bs - avg_bleu):.6f}")
        if group == "semantic_contradiction":
            print(f"INFO|insight=bertscore_limitation|group={group}|bertscore_f1={avg_bs:.6f}")
        if group == "extra_noise":
            avg_p = sum(float(r["bertscore_precision"]) for r in part) / n
            avg_r = sum(float(r["bertscore_recall"]) for r in part) / n
            print(f"INFO|insight=noise_precision_drop|group={group}|bertscore_precision={avg_p:.6f}|bertscore_recall={avg_r:.6f}")


def save_csv(rows: list[dict[str, str | float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sample_id", "experiment_type", "expected_relation", "reference", "candidate",
        "bleu", "rouge1_f", "rougeL_f", "meteor",
        "bertscore_precision", "bertscore_recall", "bertscore_f1",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = compute_rows(DEMO_SAMPLES)
    print_group_summary(rows)
    output_path = Path("outputs/day40_bertscore_scores.csv")
    save_csv(rows, output_path)
    print(f"INFO|primary_metric=bertscore_f1|average={sum(float(r['bertscore_f1']) for r in rows) / len(rows):.6f}")
    print(f"INFO|saved_csv={output_path}|rows={len(rows)}")


if __name__ == "__main__":
    main()
