"""Small conversion helpers used at the model boundary."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from enum import Enum
from typing import Any

from .models import Wgs84Coordinate


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


def to_wgs84_coordinate(
    value: Wgs84Coordinate | tuple[float, float] | Mapping[str, Any],
    *,
    field: str = "coordinate",
) -> Wgs84Coordinate:
    """Normalize coordinate inputs to a WGS84 longitude/latitude object.

    Tuple input is interpreted as `(longitude, latitude)`. Mapping input accepts
    `longitude`/`latitude`, `lon`/`lat`, or TourAPI's `mapX`/`mapY`.
    """

    if isinstance(value, Wgs84Coordinate):
        return value
    if isinstance(value, tuple):
        if len(value) != 2:
            raise ValueError(f"{field} tuple must be (longitude, latitude)")
        return Wgs84Coordinate(longitude=value[0], latitude=value[1])
    if isinstance(value, Mapping):
        lon = value.get("longitude", value.get("lon", value.get("mapX", value.get("map_x"))))
        lat = value.get("latitude", value.get("lat", value.get("mapY", value.get("map_y"))))
        if lon is None or lat is None:
            raise ValueError(
                f"{field} mapping requires longitude/latitude, lon/lat, or mapX/mapY"
            )
        return Wgs84Coordinate(longitude=float(lon), latitude=float(lat))
    raise TypeError(f"{field} must be Wgs84Coordinate, (longitude, latitude), or mapping")


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
