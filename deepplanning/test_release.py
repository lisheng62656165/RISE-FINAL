from __future__ import annotations

import json

import pytest

from deepplanning_credit import project_credit_state
from report_metrics import csv_rows, travel_metrics
from run_deepplanning_eds_eca import structural_frontier


def test_cross_round_credit_omits_literals_and_selector_prose():
    secret_id = "literal-object-7f9a"
    secret_result = "private-looking-public-result"
    credit = {
        "available": True,
        "preserve_events": [{
            "event_id": "C0-E0001",
            "tool": "query_hotel_info",
            "arguments": {"hotel_id": secret_id},
            "argument_keys": ["hotel_id"],
            "result": {"name": secret_result},
            "result_category": "SUCCESS",
        }],
        "avoid_events": [{
            "event_id": "C1-E0002",
            "tool": "query_route_info",
            "arguments": {"origin": "literal-origin"},
            "argument_keys": ["origin"],
            "result": "literal failure body",
            "result_category": "FAILURE",
        }],
        "unresolved_issue_type": "PARAMETER_GROUNDING",
        "unresolved_issue": "Recompute arguments from current public facts.",
        "reason": "free-form selector rationale must not persist",
        "supporting_event_ids": ["C0-E0001"],
    }
    projected = project_credit_state(credit)
    serialized = json.dumps(projected, sort_keys=True)
    assert secret_id not in serialized
    assert secret_result not in serialized
    assert "literal-origin" not in serialized
    assert "literal failure body" not in serialized
    assert "free-form selector rationale" not in serialized
    assert projected["preserve_events"][0] == {
        "source_event_id": "C0-E0001",
        "tool": "query_hotel_info",
        "argument_keys": ["hotel_id"],
        "result_category": "SUCCESS",
    }


def test_frontier_reprojects_untrusted_credit():
    candidate = {
        "events": [{
            "event_id": "I-E0001", "tool": "query_train_info",
            "arguments": {"train_id": "fresh-only"},
            "argument_keys": ["train_id"], "result": "full body",
            "result_category": "SUCCESS",
        }]
    }
    frontier = structural_frontier(candidate, {
        "available": True,
        "preserve_events": candidate["events"],
        "avoid_events": [],
        "reason": "do not carry me",
    })
    serialized = json.dumps(frontier, sort_keys=True)
    assert "fresh-only" not in serialized
    assert "full body" not in serialized
    assert "do not carry me" not in serialized


def evaluation_summary(plan_count: int = 120) -> dict:
    plan_ids = [str(index) for index in range(plan_count)]
    return {
        "total_test_samples": 120,
        "test_sample_ids": [str(index) for index in range(120)],
        "plan_files_found": plan_count,
        "plan_file_sample_ids": plan_ids,
        "evaluation_success_count": plan_count,
        "evaluation_failed_count": 0,
        "metrics": {
            "delivery_rate": plan_count / 120,
            "commonsense_score": 0.5,
            "personalized_score": 0.25,
            "composite_score": 0.375,
        },
        "results": [{"sample_id": task_id, "success": True} for task_id in plan_ids],
    }


def test_travel_report_requires_explicit_complete_cohort(tmp_path):
    path = tmp_path / "evaluation_summary.json"
    payload = evaluation_summary(100)
    payload["test_sample_ids"] = payload["test_sample_ids"][:-1]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="complete 120-task cohort"):
        travel_metrics(path)


def test_travel_report_exposes_paper_columns_per_language(tmp_path):
    path = tmp_path / "evaluation_summary.json"
    path.write_text(json.dumps(evaluation_summary(100)), encoding="utf-8")
    metrics = travel_metrics(path)
    assert metrics == {
        "delivery_rate": pytest.approx(83.3333333333),
        "commonsense_score": 50.0,
        "personalized_score": 25.0,
        "composite_score": 37.5,
    }
    rows = csv_rows({"rise": {"zh": metrics, "en": metrics}})
    assert list(rows[0]) == [
        "Method", "ZH Delivery", "ZH Commonsense", "ZH Personalized", "ZH Composite",
        "EN Delivery", "EN Commonsense", "EN Personalized", "EN Composite",
    ]
