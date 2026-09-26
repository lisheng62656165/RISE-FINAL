"""Validate and tabulate the official DeepPlanning Travel metrics."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_TASK_IDS = {str(index) for index in range(120)}
DEFAULT_METHODS = ("vanilla", "best_of_n", "rise")
METRIC_KEYS = ("delivery_rate", "commonsense_score", "personalized_score", "composite_score")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def percent(value: Any) -> float:
    number = float(value)
    return number * 100 if number <= 1 else number


def travel_metrics(path: Path) -> dict[str, float]:
    payload = load(path)
    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError(f"Missing metrics object in {path}")

    cohort_ids = {str(value) for value in payload.get("test_sample_ids", [])}
    if cohort_ids != EXPECTED_TASK_IDS:
        raise ValueError(f"Expected the complete 120-task cohort in {path}; got {len(cohort_ids)} IDs")

    plan_ids = [str(value) for value in payload.get("plan_file_sample_ids", [])]
    if len(plan_ids) != len(set(plan_ids)) or not set(plan_ids).issubset(cohort_ids):
        raise ValueError(f"Invalid or duplicate plan IDs in {path}")

    result_ids = [str(row.get("sample_id")) for row in payload.get("results", [])]
    if len(result_ids) != len(set(result_ids)) or set(result_ids) != set(plan_ids):
        raise ValueError(f"Evaluation results do not match delivered plans in {path}")

    total = int(payload.get("total_test_samples", -1))
    found = int(payload.get("plan_files_found", -1))
    succeeded = int(payload.get("evaluation_success_count", -1))
    failed = int(payload.get("evaluation_failed_count", -1))
    if total != 120 or found != len(plan_ids) or succeeded + failed != found:
        raise ValueError(f"Inconsistent official coverage counters in {path}")

    delivery = float(metrics.get("delivery_rate", -1))
    if abs(delivery - found / total) > 1e-9:
        raise ValueError(f"Delivery rate does not match {found}/{total} in {path}")
    missing = [key for key in METRIC_KEYS if key not in metrics]
    if missing:
        raise ValueError(f"Missing paper metrics in {path}: {', '.join(missing)}")
    return {key: percent(metrics[key]) for key in METRIC_KEYS}


def resolve_summary(root: Path, method: str, language: str) -> Path:
    path = root / method / f"travel_{language}" / "evaluation_summary.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def build_table(results: Path, methods: list[str]) -> dict[str, Any]:
    return {
        method: {
            language: travel_metrics(resolve_summary(results, method, language))
            for language in ("zh", "en")
        }
        for method in methods
    }


def csv_rows(table: dict[str, Any]) -> list[dict[str, Any]]:
    labels = {
        "delivery_rate": "Delivery",
        "commonsense_score": "Commonsense",
        "personalized_score": "Personalized",
        "composite_score": "Composite",
    }
    rows = []
    for method, languages in table.items():
        row: dict[str, Any] = {"Method": method}
        for language in ("zh", "en"):
            for key, label in labels.items():
                row[f"{language.upper()} {label}"] = languages[language][key]
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--methods", nargs="+", default=list(DEFAULT_METHODS))
    parser.add_argument("--output", type=Path, default=Path("metrics.json"))
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()

    table = build_table(args.results, args.methods)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.csv:
        rows = csv_rows(table)
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(table, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
