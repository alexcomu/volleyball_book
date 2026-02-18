from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


@lru_cache(maxsize=1)
def load_environment_config() -> dict[str, Any]:
    app_env = os.getenv("APP_ENV", "development").strip().lower() or "development"
    config_path = CONFIG_DIR / f"{app_env}.json"
    with config_path.open("r", encoding="utf-8") as file:
        return cast(dict[str, Any], json.load(file))


@lru_cache(maxsize=1)
def get_allowed_exercise_categories() -> set[str]:
    config = load_environment_config()
    values = config.get("exercise_categories", [])
    if not isinstance(values, list):
        raise ValueError("exercise_categories must be a list in configuration.")
    return {str(item).strip().lower() for item in values if str(item).strip()}
