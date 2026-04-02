"""Internationalization (i18n) support with JSON-based translations."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_LOCALES_DIR = Path(__file__).parent
_current_locale: str = "en"


@lru_cache(maxsize=8)
def _load_locale(locale: str) -> dict[str, Any]:
    """Load a locale JSON file and return its contents."""
    path = _LOCALES_DIR / f"{locale}.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
    return data


def set_locale(locale: str) -> None:
    """Set the active locale."""
    global _current_locale
    _current_locale = locale


def get_locale() -> str:
    """Get the active locale."""
    return _current_locale


def t(key: str, **kwargs: str) -> str:
    """Translate a dot-separated key using the active locale.

    Examples:
        t("status.ready")                  -> "Application is ready."
        t("sensor.reading", name="temp")   -> "Reading from temp"
    """
    data = _load_locale(_current_locale)
    parts = key.split(".")
    current: Any = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return key
    if not isinstance(current, str):
        return key
    if kwargs:
        return current.format(**kwargs)
    return current
