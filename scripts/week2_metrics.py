"""Week 2 metrics adapter used by the Day 17 batch API."""

from __future__ import annotations

from typing import Any

from scripts.day11_text_metrics import TextMetrics
import pandas as pd


class MetricsCalculator:
    """Compute a unified metric set from one CSV row.

    Expected row keys (all optional):
    - reference, candidate
    - y_true, y_pred (comma-separated ints, e.g. "1,0,1")
    - wins, losses, ties
    """

    @staticmethod
    def _parse_int_list(value: Any) -> list[int]:
        if value is None:
            return []

        if pd.isna(value):
            return []

        if isinstance(value, list):
            return [int(x) for x in value]

        text = str(value).strip()

        if not text:
            return []

        return [int(x.strip()) for x in text.split(",") if x.strip()]

    def compute(self, row: dict[str, Any]) -> dict[str, float]:
        reference = str(row.get("reference", "") or "")
        candidate = str(row.get("candidate", "") or "")

        y_true = self._parse_int_list(row.get("y_true", ""))
        y_pred = self._parse_int_list(row.get("y_pred", ""))

        wins = int(float(row.get("wins", 0) or 0))
        losses = int(float(row.get("losses", 0) or 0))
        ties = int(float(row.get("ties", 0) or 0))

        metrics = TextMetrics(
            reference=reference,
            candidate=candidate,
            y_true=y_true,
            y_pred=y_pred,
            wins=wins,
            losses=losses,
            ties=ties,
        )
        return metrics.compute_all()
