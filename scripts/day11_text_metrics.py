#!/usr/bin/env python3
"""Day 11: modular metric encapsulation for text generation and classification.

This module provides a reusable ``TextMetrics`` class that encapsulates the
metrics implemented in Day 9/Day 10:
- ROUGE-1/2/L
- BLEU-1/2
- Accuracy
- Win Rate
"""

from __future__ import annotations

from collections import Counter
import importlib
import importlib.util
from math import exp, log, sqrt


class TextMetrics:
    """Unified metric calculator for text, classification, and win/loss statistics.

    Parameters
    ----------
    reference : str
        Reference text for ROUGE/BLEU computation.
    candidate : str
        Candidate text for ROUGE/BLEU computation.
    y_true : list[int]
        Ground-truth labels for accuracy computation.
    y_pred : list[int]
        Predicted labels for accuracy computation.
    wins : int
        Number of wins for win-rate computation.
    losses : int
        Number of losses for win-rate computation.
    ties : int, default=0
        Number of ties for win-rate computation.

    Notes
    -----
    - Empty text/list inputs are accepted and return ``0.0`` where applicable.
    - Shape/value validation for methods is performed at computation time.
    """

    def __init__(
        self,
        reference: str,
        candidate: str,
        y_true: list[int],
        y_pred: list[int],
        wins: int,
        losses: int,
        ties: int = 0,
    ) -> None:
        self.reference = reference
        self.candidate = candidate
        self.y_true = y_true
        self.y_pred = y_pred
        self.wins = wins
        self.losses = losses
        self.ties = ties

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Split text by whitespace.

        Parameters
        ----------
        text : str
            Raw text.

        Returns
        -------
        list[str]
            Token list; empty when input is empty/whitespace-only.
        """
        return text.strip().split()

    @staticmethod
    def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
        """Generate n-grams.

        Raises
        ------
        ValueError
            If ``n <= 0``.
        """
        if n <= 0:
            raise ValueError("n must be >= 1")
        if len(tokens) < n:
            return []
        return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]

    def compute_rouge(self, n: int) -> float:
        """Compute ROUGE-N recall.

        Returns
        -------
        float
            ROUGE-N recall in [0, 1]. Returns 0.0 when reference has no n-grams.

        Raises
        ------
        ValueError
            If ``n <= 0``.
        """
        ref_counts = Counter(self.ngrams(self.tokenize(self.reference), n))
        cand_counts = Counter(self.ngrams(self.tokenize(self.candidate), n))
        ref_total = sum(ref_counts.values())
        if ref_total == 0:
            return 0.0
        overlap = sum(min(count, cand_counts[gram]) for gram, count in ref_counts.items())
        return overlap / ref_total

    @staticmethod
    def lcs_length(a: list[str], b: list[str]) -> int:
        """Compute length of longest common subsequence (LCS)."""
        dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        for i in range(1, len(a) + 1):
            for j in range(1, len(b) + 1):
                if a[i - 1] == b[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        return dp[-1][-1]

    def compute_rouge_l(self) -> float:
        """Compute ROUGE-L recall based on LCS.

        Returns 0.0 when reference is empty.
        """
        ref_tokens = self.tokenize(self.reference)
        if not ref_tokens:
            return 0.0
        return self.lcs_length(ref_tokens, self.tokenize(self.candidate)) / len(ref_tokens)

    def compute_bleu(self, max_n: int) -> float:
        """Compute BLEU score up to ``max_n`` n-gram precision.

        Raises
        ------
        ValueError
            If ``max_n <= 0``.
        """
        if max_n <= 0:
            raise ValueError("max_n must be >= 1")

        ref_tokens = self.tokenize(self.reference)
        cand_tokens = self.tokenize(self.candidate)
        cand_len = len(cand_tokens)
        if cand_len == 0:
            return 0.0

        precisions: list[float] = []
        for n in range(1, max_n + 1):
            cand_counts = Counter(self.ngrams(cand_tokens, n))
            total = sum(cand_counts.values())
            if total == 0:
                return 0.0
            ref_counts = Counter(self.ngrams(ref_tokens, n))
            matched = sum(min(count, ref_counts[gram]) for gram, count in cand_counts.items())
            precisions.append(matched / total)

        if not precisions or min(precisions) == 0:
            return 0.0

        geo_mean = exp(sum(log(p) for p in precisions) / len(precisions))
        ref_len = len(ref_tokens)
        brevity_penalty = 1.0 if cand_len > ref_len else exp(1 - ref_len / cand_len)
        return brevity_penalty * geo_mean

    def compute_accuracy(self) -> float:
        """Compute classification accuracy.

        Raises
        ------
        ValueError
            If ``len(y_true) != len(y_pred)``.
        """
        if len(self.y_true) != len(self.y_pred):
            raise ValueError("y_true and y_pred must have same length")
        if not self.y_true:
            return 0.0
        return sum(int(t == p) for t, p in zip(self.y_true, self.y_pred)) / len(self.y_true)

    def compute_win_rate(self, half_tie: bool = True) -> float:
        """Compute win rate with optional half-tie credit.

        Parameters
        ----------
        half_tie : bool, default=True
            If True, each tie contributes 0.5 win; else contributes 0.0.

        Raises
        ------
        ValueError
            If wins/losses/ties contains negative values.
        """
        if self.wins < 0 or self.losses < 0 or self.ties < 0:
            raise ValueError("wins, losses, ties must be >= 0")
        total = self.wins + self.losses + self.ties
        if total == 0:
            return 0.0
        return (self.wins + (0.5 * self.ties if half_tie else 0.0)) / total

    def compute_all(self) -> dict[str, float]:
        """Compute all Day 10 metrics with unified output keys."""
        return {
            "rouge_1": self.compute_rouge(1),
            "rouge_2": self.compute_rouge(2),
            "rouge_l": self.compute_rouge_l(),
            "bleu_1": self.compute_bleu(1),
            "bleu_2": self.compute_bleu(2),
            "accuracy": self.compute_accuracy(),
            "win_rate_half_tie": self.compute_win_rate(half_tie=True),
            "win_rate_no_tie_credit": self.compute_win_rate(half_tie=False),
        }

    @staticmethod
    def validate_with_optional_libraries(reference: str, candidate: str) -> tuple[dict[str, float], list[str]]:
        """Optionally validate BLEU/ROUGE with external libraries.

        Returns
        -------
        tuple[dict[str, float], list[str]]
            A tuple of (library_results, notes). Missing packages are recorded in notes.
        """
        results: dict[str, float] = {}
        notes: list[str] = []

        if importlib.util.find_spec("nltk") is not None:
            try:
                nltk_bleu = importlib.import_module("nltk.translate.bleu_score")
                sentence_bleu = getattr(nltk_bleu, "sentence_bleu")
                ref_tokens = reference.strip().split()
                cand_tokens = candidate.strip().split()
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
    """Run Day 10 sample verification and boundary/exception checks for Day 11 class."""
    metrics = TextMetrics(
        reference="the cat is on the mat",
        candidate="the cat sat on the mat",
        y_true=[1, 0, 1, 1, 0, 0, 1, 0],
        y_pred=[1, 1, 1, 1, 0, 0, 0, 0],
        wins=6,
        losses=3,
        ties=1,
    )

    computed = metrics.compute_all()
    manual = {
        "rouge_1": 5 / 6,
        "rouge_2": 3 / 5,
        "rouge_l": 5 / 6,
        "bleu_1": 5 / 6,
        "bleu_2": sqrt((5 / 6) * (3 / 5)),
        "accuracy": 6 / 8,
        "win_rate_half_tie": (6 + 0.5) / 10,
        "win_rate_no_tie_credit": 6 / 10,
    }

    print("=== Day 11 TextMetrics compute_all verification ===")
    print("metric\tcomputed\tmanual\tdelta")
    for key, value in computed.items():
        delta = abs(value - manual[key])
        print(f"{key}\t{value:.10f}\t{manual[key]:.10f}\t{delta:.10f}")

    print("\n=== Boundary checks ===")
    boundary_cases = [
        TextMetrics("", "a", [], [], 0, 0, 0).compute_rouge(1),
        TextMetrics("a", "", [], [], 0, 0, 0).compute_rouge(1),
        TextMetrics("", "a", [], [], 0, 0, 0).compute_rouge_l(),
        TextMetrics("", "a", [], [], 0, 0, 0).compute_bleu(1),
        TextMetrics("a", "", [], [], 0, 0, 0).compute_bleu(1),
        TextMetrics("a b", "a b", [], [], 0, 0, 0).compute_bleu(3),
        TextMetrics("", "", [], [], 0, 0, 0).compute_accuracy(),
        TextMetrics("", "", [], [], 0, 0, 0).compute_win_rate(),
    ]
    print(f"boundary_values={boundary_cases}")

    print("\n=== Exception checks ===")
    exception_cases = [
        ("compute_rouge(0)", lambda: TextMetrics("a", "a", [], [], 0, 0).compute_rouge(0), ValueError),
        ("compute_bleu(0)", lambda: TextMetrics("a", "a", [], [], 0, 0).compute_bleu(0), ValueError),
        (
            "compute_accuracy(len mismatch)",
            lambda: TextMetrics("", "", [1], [1, 0], 0, 0).compute_accuracy(),
            ValueError,
        ),
        ("compute_win_rate(negative)", lambda: TextMetrics("", "", [], [], -1, 1).compute_win_rate(), ValueError),
    ]

    for name, fn, exc in exception_cases:
        try:
            fn()
            print(f"{name}: FAIL(no exception)")
        except exc:
            print(f"{name}: PASS({exc.__name__})")

    lib_results, lib_notes = TextMetrics.validate_with_optional_libraries(
        metrics.reference,
        metrics.candidate,
    )
    print("\n=== Optional library validation ===")
    if lib_results:
        for k, v in lib_results.items():
            print(f"{k}={v:.10f}")
    else:
        print("no_library_results")
    for note in lib_notes:
        print(f"note={note}")


if __name__ == "__main__":
    main()
