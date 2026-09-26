"""Load trajectory artifacts keyed by task identifier.

The production loop receives Vanilla A trajectories as immutable input
artifacts. It scans one directory, skips reports and errors, validates unique
task keys, and returns the mapping used by the runner. It does not score or
select candidates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


IGNORED_NAMES = {"summary.json", "score_summary.json", "report.json", "report_scores.json"}


def read_rows(directory: Path) -> dict[str, dict[str, Any]]:
    """Load one completed trajectory per task key from an artifact directory."""
    rows = {}
    for path in sorted(directory.glob("*.json")):
        if path.name in IGNORED_NAMES or path.name.endswith(
            (".error.json", "summary.json", "report.json", "report_scores.json")
        ):
            continue
        row = json.loads(path.read_text(encoding="utf-8"))
        key = str(row.get("task_key") or "")
        if not key or key in rows:
            raise ValueError(f"invalid or duplicate task_key in {path}")
        rows[key] = row
    return rows
