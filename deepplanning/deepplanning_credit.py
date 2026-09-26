"""Structural, source-constrained event credit shared by DeepPlanning adapters."""
from __future__ import annotations

from typing import Any, Mapping


EVENT_SHAPE_FIELDS = (
    "operation",
    "event_class",
    "tool",
    "entity_fields",
    "argument_keys",
    "result_category",
    "interaction_type",
)


def project_event_shape(event: Mapping[str, Any]) -> dict[str, Any]:
    """Retain event provenance and structural shape, never literal values."""
    projected: dict[str, Any] = {
        "source_event_id": str(event.get("source_event_id") or event.get("event_id") or ""),
    }
    for field in EVENT_SHAPE_FIELDS:
        if field not in event:
            continue
        value = event[field]
        if field in {"entity_fields", "argument_keys"}:
            value = sorted(str(item) for item in (value or []))
        elif value is not None:
            value = str(value)
        projected[field] = value
    return projected


def project_credit_state(credit: Mapping[str, Any] | None) -> dict[str, Any]:
    """Project selector credit onto the cross-round representation in the paper."""
    if not credit or not credit.get("available"):
        return {"available": False, "public_only": True, "outcome_used": False}
    return {
        "available": True,
        "preserve_events": [
            project_event_shape(event) for event in credit.get("preserve_events", [])
        ][:6],
        "avoid_events": [
            project_event_shape(event) for event in credit.get("avoid_events", [])
        ][:6],
        "unresolved_issue_type": str(credit.get("unresolved_issue_type") or "NONE"),
        "unresolved_issue": str(credit.get("unresolved_issue") or ""),
        "supporting_event_ids": [
            str(event_id) for event_id in credit.get("supporting_event_ids", [])
        ],
        "literal_replay": False,
        "public_only": True,
        "outcome_used": False,
    }
