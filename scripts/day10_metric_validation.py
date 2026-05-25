#!/usr/bin/env python3
from __future__ import annotations

from math import sqrt

from scripts.day9_text_metrics import accuracy, bleu, rouge_l, rouge_n, win_rate


def fmt(x: float) -> str:
    return f"{x:.10f}"


def print_comparison_table() -> dict[str, tuple[float, float, float]]:
    reference = "the cat is on the mat"
    candidate = "the cat sat on the mat"
    y_true = [1, 0, 1, 1, 0, 0, 1, 0]
    y_pred = [1, 1, 1, 1, 0, 0, 0, 0]
    wins, losses, ties = 6, 3, 1

    results = {
        "ROUGE-1": rouge_n(reference, candidate, 1),
        "ROUGE-2": rouge_n(reference, candidate, 2),
        "ROUGE-L": rouge_l(reference, candidate),
        "BLEU-1": bleu(reference, candidate, 1),
        "BLEU-2": bleu(reference, candidate, 2),
        "Accuracy": accuracy(y_true, y_pred),
        "WinRate(half tie)": win_rate(wins, losses, ties, half_tie=True),
        "WinRate(no tie credit)": win_rate(wins, losses, ties, half_tie=False),
    }

    expected = {
        "ROUGE-1": 5 / 6,
        "ROUGE-2": 3 / 5,
        "ROUGE-L": 5 / 6,
        "BLEU-1": 5 / 6,
        "BLEU-2": sqrt((5 / 6) * (3 / 5)),
        "Accuracy": 6 / 8,
        "WinRate(half tie)": (6 + 0.5) / 10,
        "WinRate(no tie credit)": 6 / 10,
    }

    print("=== Day 10 Metric Validation: main sample ===")
    print("metric\tcomputed\texpected\tdelta")
    rows: dict[str, tuple[float, float, float]] = {}
    for k, v in results.items():
        delta = abs(v - expected[k])
        rows[k] = (v, expected[k], delta)
        print(f"{k}\t{fmt(v)}\t{fmt(expected[k])}\t{fmt(delta)}")
    return rows


def run_boundary_checks() -> None:
    print("\n=== Boundary/edge checks ===")

    checks: list[tuple[str, float, float]] = [
        ("rouge_n('', 'a', 1)", rouge_n("", "a", 1), 0.0),
        ("rouge_n('a', '', 1)", rouge_n("a", "", 1), 0.0),
        ("rouge_l('', 'a')", rouge_l("", "a"), 0.0),
        ("bleu('', 'a', 1)", bleu("", "a", 1), 0.0),
        ("bleu('a', '', 1)", bleu("a", "", 1), 0.0),
        ("bleu('a b', 'a b', 3)", bleu("a b", "a b", 3), 0.0),
        ("accuracy([], [])", accuracy([], []), 0.0),
        ("win_rate(0, 0, 0)", win_rate(0, 0, 0), 0.0),
    ]

    for name, got, exp in checks:
        print(
            f"{name}\tgot={fmt(got)}\texpected={fmt(exp)}\tdelta={fmt(abs(got - exp))}"
        )

    exception_cases = [
        ("rouge_n('a', 'a', 0)", lambda: rouge_n("a", "a", 0), ValueError),
        ("bleu('a', 'a', 0)", lambda: bleu("a", "a", 0), ValueError),
        ("accuracy([1], [1, 0])", lambda: accuracy([1], [1, 0]), ValueError),
        ("win_rate(-1, 1, 0)", lambda: win_rate(-1, 1, 0), ValueError),
    ]

    for name, fn, exc in exception_cases:
        try:
            fn()
            print(f"{name}\tERROR=no exception raised")
        except exc:
            print(f"{name}\tOK={exc.__name__}")


def main() -> None:
    rows = print_comparison_table()
    all_exact = all(delta <= 1e-12 for _, _, delta in rows.values())
    print(f"\nRESULT|main_sample_match={'PASS' if all_exact else 'FAIL'}")
    run_boundary_checks()


if __name__ == "__main__":
    # uv run python -m scripts.day10_metric_validation
    main()
