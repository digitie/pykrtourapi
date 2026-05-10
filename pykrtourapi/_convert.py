"""Small conversion helpers used at the model boundary."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any


def strip_or_none(value: object) -> str | None:
    """Return a stripped string, treating blanks and missing values as None."""

    if value is None:
        return None
    text = str(value).strip()
    return text or None


def enum_value(value: object) -> object:
    """Return an enum's value while leaving regular objects unchanged."""

    if isinstance(value, Enum):
        return value.value
    return value


def to_int_or_none(value: object) -> int | None:
    """Convert numeric-looking values to int, otherwise return None."""

    text = strip_or_none(value)
    if text is None:
        return None
    try:
        return int(text)
    except ValueError:
        try:
            return int(float(text))
        except ValueError:
            return None


def to_float_or_none(value: object) -> float | None:
    """Convert numeric-looking values to float, otherwise return None."""

    text = strip_or_none(value)
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def to_yyyymmdd(value: str | date | datetime | None, *, field: str) -> str | None:
    """Normalize a date-like value to YYYYMMDD."""

    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y%m%d")
    if isinstance(value, date):
        return value.strftime("%Y%m%d")
    text = value.strip()
    if len(text) != 8 or not text.isdigit():
        raise ValueError(f"{field} must be YYYYMMDD")
    return text


def yn(value: bool | str | None) -> str | None:
    """Normalize a Python bool or Y/N-like string to TourAPI's Y/N form."""

    if value is None:
        return None
    if isinstance(value, bool):
        return "Y" if value else "N"
    text = value.strip().upper()
    if text not in {"Y", "N"}:
        raise ValueError("Y/N value must be True, False, 'Y', or 'N'")
    return text


def without_none(params: dict[str, Any]) -> dict[str, Any]:
    """Drop None values while preserving falsey but meaningful values."""

    return {key: value for key, value in params.items() if value is not None}
