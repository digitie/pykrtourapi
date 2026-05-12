"""KST datetime helpers for TourAPI timestamps."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

KST: tzinfo
try:
    KST = ZoneInfo("Asia/Seoul")
except ZoneInfoNotFoundError:  # pragma: no cover - depends on platform tzdata
    KST = timezone(timedelta(hours=9), "Asia/Seoul")


def parse_tour_datetime(value: object) -> datetime | None:
    """Parse TourAPI timestamps such as YYYYMMDDHHMMSS or YYYYMMDD as KST."""

    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if len(text) >= 14 and text[:14].isdigit():
            return datetime.strptime(text[:14], "%Y%m%d%H%M%S").replace(tzinfo=KST)
        if len(text) == 8 and text.isdigit():
            return datetime.strptime(text, "%Y%m%d").replace(tzinfo=KST)
    except ValueError:
        return None
    return None
