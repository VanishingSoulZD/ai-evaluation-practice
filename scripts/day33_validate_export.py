import json
from pathlib import Path

REQUIRED_ROOT = ["id", "data", "meta", "annotations"]
REQUIRED_DATA = ["sample_id", "task_type", "source_dataset"]
REQUIRED_RESULT_KEYS = ["label", "final_answer", "evidence_span", "rule_id"]


def _extract_result_map(annotation: dict) -> dict:
    result_map = {}
    for item in annotation.get("result", []):
        name = item.get("from_name")
        value = item.get("value", {})
        if not name:
            continue
        if "choices" in value and value["choices"]:
            result_map[name] = value["choices"][0]
        elif "text" in value and value["text"]:
            result_map[name] = value["text"][0]
        else:
            result_map[name] = ""
    return result_map


def main() -> None:
    path = Path("outputs/day33_label_studio_export.sample.json")
    records = json.loads(path.read_text(encoding="utf-8"))

    missing = []
    print(f"Loaded {len(records)} tasks from {path}")

    for idx, task in enumerate(records, start=1):
        for key in REQUIRED_ROOT:
            if key not in task:
                missing.append(f"task#{idx} missing root key: {key}")

        data = task.get("data", {})
        for key in REQUIRED_DATA:
            if not data.get(key):
                missing.append(f"task#{idx} missing data.{key}")

        annotations = [a for a in task.get("annotations", []) if not a.get("was_cancelled", False)]
        if not annotations:
            missing.append(f"task#{idx} has no active annotations")
            continue

        latest = sorted(annotations, key=lambda a: a.get("updated_at", ""))[-1]
        result_map = _extract_result_map(latest)

        for key in REQUIRED_RESULT_KEYS:
            if key not in result_map:
                missing.append(f"task#{idx} missing result field: {key}")

        print(
            f"task#{idx}: sample_id={data.get('sample_id')} "
            f"task_type={data.get('task_type')} "
            f"label={result_map.get('label', '')} "
            f"final_answer={result_map.get('final_answer', '')}"
        )

    if missing:
        print("\nValidation errors:")
        for err in missing:
            print(f"- {err}")
        raise SystemExit(1)

    print("\nValidation passed.")


if __name__ == "__main__":
    main()
