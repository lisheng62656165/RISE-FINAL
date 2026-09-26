from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_MODEL_CONFIG = os.environ.get("DEEPPLANNING_MODEL")
DEFAULT_MODELS_CONFIG = (
    Path(__file__).resolve().parents[1] / "models_config.json"
)


def resolve_model_identity(models_config_path: Path, config_name: str) -> dict[str, Any]:
    payload = json.loads(models_config_path.read_text(encoding="utf-8"))
    config = (payload.get("models") or {}).get(config_name)
    if not isinstance(config, dict):
        raise ValueError(f"Missing model config: {config_name}")
    return {
        "model_config": config_name,
        "api_model": str(config.get("model_name", config_name)),
    }
