from __future__ import annotations

from datetime import date

import pytest

from pykrtourapi import Wgs84Coordinate
from pykrtourapi._convert import (
    strip_or_none,
    to_float_or_none,
    to_int_or_none,
    to_wgs84_coordinate,
    to_yyyymmdd,
    yn,
)
from pykrtourapi._time import parse_tour_datetime


def test_strip_and_numeric_conversions():
    assert strip_or_none("  서울  ") == "서울"
    assert strip_or_none(" ") is None
    assert to_int_or_none("12.0") == 12
    assert to_float_or_none("37.5") == 37.5
    assert to_float_or_none("not-number") is None


def test_date_and_yn_conversions():
    assert to_yyyymmdd(date(2026, 4, 30), field="event_start_date") == "20260430"
    assert to_yyyymmdd("20260430", field="event_start_date") == "20260430"
    with pytest.raises(ValueError):
        to_yyyymmdd("2026-04-30", field="event_start_date")
    assert yn(True) == "Y"
    assert yn(False) == "N"
    assert yn("y") == "Y"
    with pytest.raises(ValueError):
        yn("yes")


def test_wgs84_coordinate_normalization():
    coordinate = Wgs84Coordinate(longitude=126.9769, latitude=37.5796)

    assert coordinate.map_x == 126.9769
    assert coordinate.map_y == 37.5796
    assert coordinate.lonlat == (126.9769, 37.5796)
    assert coordinate.latlon == (37.5796, 126.9769)
    assert coordinate.to_tourapi_params() == {"mapX": 126.9769, "mapY": 37.5796}
    assert to_wgs84_coordinate((126.9, 37.5)).longitude == 126.9
    assert to_wgs84_coordinate({"lon": 126.9, "lat": 37.5}).latitude == 37.5
    assert to_wgs84_coordinate({"mapX": "126.9", "mapY": "37.5"}).lonlat == (126.9, 37.5)

    with pytest.raises(ValueError, match="longitude"):
        Wgs84Coordinate(longitude=181, latitude=37.5)
    with pytest.raises(ValueError, match="latitude"):
        Wgs84Coordinate(longitude=126.9, latitude=91)
    with pytest.raises(ValueError, match="mapping"):
        to_wgs84_coordinate({"x": 126.9, "y": 37.5})


def test_parse_tour_datetime():
    parsed = parse_tour_datetime("20260430123456")
    assert parsed is not None
    assert parsed.year == 2026
    assert parsed.month == 4
    assert parsed.tzinfo is not None
    assert parse_tour_datetime("20260430").hour == 0  # type: ignore[union-attr]
    assert parse_tour_datetime("bad") is None
