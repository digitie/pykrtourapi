from __future__ import annotations

from datetime import date

import pytest

from pykrtourapi._convert import strip_or_none, to_float_or_none, to_int_or_none, to_yyyymmdd, yn
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


def test_parse_tour_datetime():
    parsed = parse_tour_datetime("20260430123456")
    assert parsed is not None
    assert parsed.year == 2026
    assert parsed.month == 4
    assert parsed.tzinfo is not None
    assert parse_tour_datetime("20260430").hour == 0  # type: ignore[union-attr]
    assert parse_tour_datetime("bad") is None
