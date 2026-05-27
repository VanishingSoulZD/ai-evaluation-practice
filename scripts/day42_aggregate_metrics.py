#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

MAX_ROWS = 30
OUTPUT_PATH = Path('outputs/day42_final_metrics.csv')

INPUT_SPECS = {
    'bleu': {'path': Path('outputs/day37_bleu_scores.csv'), 'column': 'bleu'},
    'rougeL_f': {'path': Path('outputs/day38_rouge_scores.csv'), 'column': 'rougeL'},
    'meteor': {'path': Path('outputs/day39_meteor_scores.csv'), 'column': 'meteor'},
    'bertscore_f1': {'path': Path('outputs/day40_bertscore_scores.csv'), 'column': 'bertscore_f1'},
}


def read_metric_rows(path: Path, metric_name: str, metric_column: str, max_rows: int) -> dict[str, str]:
    if not path.exists():
        print(f'WARNING|missing_file|metric={metric_name}|path={path}')
        return {}

    with path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print(f'WARNING|empty_or_invalid_csv|metric={metric_name}|path={path}')
            return {}
        if 'sample_id' not in reader.fieldnames:
            print(f"WARNING|missing_column|metric={metric_name}|column=sample_id|path={path}")
            return {}
        if metric_column not in reader.fieldnames:
            print(f"WARNING|missing_column|metric={metric_name}|column={metric_column}|path={path}")
            return {}

        rows: dict[str, str] = {}
        for idx, row in enumerate(reader):
            if idx >= max_rows:
                break
            sample_id = (row.get('sample_id') or '').strip()
            if not sample_id:
                continue
            rows[sample_id] = (row.get(metric_column) or '').strip()

    print(f'INFO|loaded|metric={metric_name}|rows={len(rows)}|path={path}')
    return rows


def build_aggregate(max_rows: int = MAX_ROWS) -> list[dict[str, str]]:
    metric_maps: dict[str, dict[str, str]] = {}
    for metric_name, spec in INPUT_SPECS.items():
        metric_maps[metric_name] = read_metric_rows(spec['path'], metric_name, spec['column'], max_rows)

    all_sample_ids: list[str] = sorted({sid for metric_rows in metric_maps.values() for sid in metric_rows.keys()})
    if len(all_sample_ids) > max_rows:
        all_sample_ids = all_sample_ids[:max_rows]

    output_rows: list[dict[str, str]] = []
    for sample_id in all_sample_ids:
        output_rows.append(
            {
                'sample_id': sample_id,
                'bleu': metric_maps['bleu'].get(sample_id, ''),
                'rougeL_f': metric_maps['rougeL_f'].get(sample_id, ''),
                'meteor': metric_maps['meteor'].get(sample_id, ''),
                'bertscore_f1': metric_maps['bertscore_f1'].get(sample_id, ''),
            }
        )
    return output_rows


def write_output(rows: list[dict[str, str]]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ['sample_id', 'bleu', 'rougeL_f', 'meteor', 'bertscore_f1']

    with OUTPUT_PATH.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'INFO|written|path={OUTPUT_PATH}|rows={len(rows)}')


def print_preview(rows: list[dict[str, str]], limit: int = 5) -> None:
    print('INFO|summary|preview_start')
    for row in rows[:limit]:
        print(
            '|'.join(
                [
                    'ROW',
                    f"sample_id={row['sample_id']}",
                    f"bleu={row['bleu']}",
                    f"rougeL_f={row['rougeL_f']}",
                    f"meteor={row['meteor']}",
                    f"bertscore_f1={row['bertscore_f1']}",
                ]
            )
        )
    print('INFO|summary|preview_end')


def main() -> None:
    rows = build_aggregate(MAX_ROWS)
    write_output(rows)
    print_preview(rows)


if __name__ == '__main__':
    main()
