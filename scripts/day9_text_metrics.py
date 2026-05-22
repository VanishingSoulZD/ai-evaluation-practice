#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import importlib
import importlib.util
from math import exp, log


def tokenize(text: str) -> list[str]:
    return text.strip().split()


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0:
        raise ValueError("n must be >= 1")
    if len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def rouge_n(reference: str, candidate: str, n: int = 1) -> float:
    ref_counts = Counter(ngrams(tokenize(reference), n))
    cand_counts = Counter(ngrams(tokenize(candidate), n))
    ref_total = sum(ref_counts.values())
    if ref_total == 0:
        return 0.0
    overlap = sum(min(count, cand_counts[gram]) for gram, count in ref_counts.items())
    return overlap / ref_total


def lcs_length(a: list[str], b: list[str]) -> int:
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def rouge_l(reference: str, candidate: str) -> float:
    ref_tokens = tokenize(reference)
    if not ref_tokens:
        return 0.0
    return lcs_length(ref_tokens, tokenize(candidate)) / len(ref_tokens)


def bleu(reference: str, candidate: str, max_n: int = 2) -> float:
    if max_n <= 0:
        raise ValueError("max_n must be >= 1")

    ref_tokens = tokenize(reference)
    cand_tokens = tokenize(candidate)
    cand_len = len(cand_tokens)

    if cand_len == 0:
        return 0.0

    precisions: list[float] = []
    for n in range(1, max_n + 1):
        cand_counts = Counter(ngrams(cand_tokens, n))
        total = sum(cand_counts.values())
        if total == 0:
            return 0.0
        ref_counts = Counter(ngrams(ref_tokens, n))
        matched = sum(min(count, ref_counts[gram]) for gram, count in cand_counts.items())
        precisions.append(matched / total)

    if not precisions or min(precisions) == 0:
        return 0.0

    geo_mean = exp(sum(log(p) for p in precisions) / len(precisions))
    ref_len = len(ref_tokens)
    brevity_penalty = 1.0 if cand_len > ref_len else exp(1 - ref_len / cand_len)
    return brevity_penalty * geo_mean


def accuracy(y_true: list[int], y_pred: list[int]) -> float:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have same length")
    if not y_true:
        return 0.0
    return sum(int(t == p) for t, p in zip(y_true, y_pred)) / len(y_true)


def win_rate(wins: int, losses: int, ties: int = 0, half_tie: bool = True) -> float:
    if wins < 0 or losses < 0 or ties < 0:
        raise ValueError("wins, losses, ties must be >= 0")
    total = wins + losses + ties
    if total == 0:
        return 0.0
    return (wins + (0.5 * ties if half_tie else 0.0)) / total


def compute_demo_metrics() -> dict[str, float]:
    ref = "the cat is on the mat"
    cand = "the cat sat on the mat"
    y_true = [1, 0, 1, 1, 0, 0, 1, 0]
    y_pred = [1, 1, 1, 1, 0, 0, 0, 0]
    wins, losses, ties = 6, 3, 1

    return {
        "rouge_1": rouge_n(ref, cand, n=1),
        "rouge_2": rouge_n(ref, cand, n=2),
        "rouge_l": rouge_l(ref, cand),
        "bleu_1": bleu(ref, cand, max_n=1),
        "bleu_2": bleu(ref, cand, max_n=2),
        "accuracy": accuracy(y_true, y_pred),
        "win_rate_half_tie": win_rate(wins, losses, ties, half_tie=True),
        "win_rate_no_tie_credit": win_rate(wins, losses, ties, half_tie=False),
    }


def optional_library_validation(reference: str, candidate: str) -> tuple[dict[str, float], list[str]]:
    results: dict[str, float] = {}
    notes: list[str] = []

    if importlib.util.find_spec("nltk") is not None:
        try:
            nltk_bleu = importlib.import_module("nltk.translate.bleu_score")
            sentence_bleu = getattr(nltk_bleu, "sentence_bleu")
            ref_tokens = tokenize(reference)
            cand_tokens = tokenize(candidate)
            results["lib_nltk_bleu_1"] = sentence_bleu([ref_tokens], cand_tokens, weights=(1, 0, 0, 0))
            results["lib_nltk_bleu_2"] = sentence_bleu([ref_tokens], cand_tokens, weights=(0.5, 0.5, 0, 0))
        except Exception as exc:
            notes.append(f"nltk_available_but_unusable: {exc.__class__.__name__}")
    else:
        notes.append("nltk_not_installed")

    if importlib.util.find_spec("rouge_score") is not None:
        try:
            rouge_scorer = importlib.import_module("rouge_score.rouge_scorer")
            scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)
            score = scorer.score(reference, candidate)
            results["lib_rouge_score_rouge1_recall"] = score["rouge1"].recall
            results["lib_rouge_score_rouge2_recall"] = score["rouge2"].recall
            results["lib_rouge_score_rougeL_recall"] = score["rougeL"].recall
        except Exception as exc:
            notes.append(f"rouge_score_available_but_unusable: {exc.__class__.__name__}")
    else:
        notes.append("rouge_score_not_installed")

    return results, notes


def main() -> None:
    ref = "the cat is on the mat"
    cand = "the cat sat on the mat"

    metrics = compute_demo_metrics()
    manual_targets = {
        "rouge_1": 5 / 6,
        "rouge_2": 3 / 5,
        "rouge_l": 5 / 6,
        "bleu_1": 5 / 6,
        "bleu_2": ((5 / 6) * (3 / 5)) ** 0.5,
        "accuracy": 6 / 8,
        "win_rate_half_tie": (6 + 0.5) / 10,
        "win_rate_no_tie_credit": 6 / 10,
    }

    print("INFO|reference=the cat is on the mat")
    print("INFO|candidate=the cat sat on the mat")

    for key, value in metrics.items():
        print(f"METRIC|{key}|{value:.6f}")

    for key, target in manual_targets.items():
        delta = abs(metrics[key] - target)
        print(f"CHECK|{key}|expected={target:.6f}|delta={delta:.6f}")

    lib_results, lib_notes = optional_library_validation(ref, cand)
    if lib_results:
        print("LIB_VALIDATION|status=enabled|note=library_results_are_for_cross_check_only")
        for key, value in lib_results.items():
            print(f"LIB_METRIC|{key}|{value:.6f}")
    else:
        print("LIB_VALIDATION|status=skipped|note=no_valid_library_result_generated")

    for note in lib_notes:
        print(f"LIB_NOTE|{note}")


if __name__ == "__main__":
    main()
