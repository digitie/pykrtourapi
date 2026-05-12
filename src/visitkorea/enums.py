"""Public constants and enum helpers."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class MobileOS(StrEnum):
    """TourAPI MobileOS parameter values."""

    IOS = "IOS"
    ANDROID = "AND"
    WEB = "WEB"
    WINDOWS_PHONE = "WIN"
    ETC = "ETC"


class Language(StrEnum):
    """TourAPI language service selectors."""

    KOREAN = "ko"
    ENGLISH = "en"
    JAPANESE = "ja"
    SIMPLIFIED_CHINESE = "zh-cn"
    TRADITIONAL_CHINESE = "zh-tw"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    RUSSIAN = "ru"


class Arrange(StrEnum):
    """TourAPI arrange parameter values."""

    TITLE = "A"
    MODIFIED = "C"
    CREATED = "D"
    DISTANCE = "E"
    TITLE_WITH_IMAGE = "O"
    MODIFIED_WITH_IMAGE = "Q"
    CREATED_WITH_IMAGE = "R"
    DISTANCE_WITH_IMAGE = "S"


class ContentType(StrEnum):
    """KorService2 content type IDs."""

    TOURIST_ATTRACTION = "12"
    CULTURAL_FACILITY = "14"
    FESTIVAL = "15"
    TRAVEL_COURSE = "25"
    LEISURE_SPORTS = "28"
    ACCOMMODATION = "32"
    SHOPPING = "38"
    RESTAURANT = "39"


class AreaCode(StrEnum):
    """KorService2 areaCode values."""

    SEOUL = "1"
    INCHEON = "2"
    DAEJEON = "3"
    DAEGU = "4"
    GWANGJU = "5"
    BUSAN = "6"
    ULSAN = "7"
    SEJONG = "8"
    GYEONGGI = "31"
    GANGWON = "32"
    CHUNGBUK = "33"
    CHUNGNAM = "34"
    GYEONGBUK = "35"
    GYEONGNAM = "36"
    JEONBUK = "37"
    JEONNAM = "38"
    JEJU = "39"


CONTENT_TYPE_LABELS: Final[dict[str, str]] = {
    "12": "관광지",
    "14": "문화시설",
    "15": "축제/공연/행사",
    "25": "여행코스",
    "28": "레포츠",
    "32": "숙박",
    "38": "쇼핑",
    "39": "음식점",
}

AREA_CODE_LABELS: Final[dict[str, str]] = {
    "1": "서울",
    "2": "인천",
    "3": "대전",
    "4": "대구",
    "5": "광주",
    "6": "부산",
    "7": "울산",
    "8": "세종",
    "31": "경기",
    "32": "강원",
    "33": "충북",
    "34": "충남",
    "35": "경북",
    "36": "경남",
    "37": "전북",
    "38": "전남",
    "39": "제주",
}

SERVICE_NAME_BY_LANGUAGE: Final[dict[str, str]] = {
    "ko": "KorService2",
    "en": "EngService2",
    "ja": "JpnService2",
    "jp": "JpnService2",
    "zh-cn": "ChsService2",
    "zh": "ChsService2",
    "zh-tw": "ChtService2",
    "de": "GerService2",
    "fr": "FreService2",
    "es": "SpnService2",
    "ru": "RusService2",
}


def content_type_label(value: str | ContentType | None) -> str | None:
    """Return the Korean label for a KorService2 content type ID."""

    if value is None:
        return None
    return CONTENT_TYPE_LABELS.get(str(value))


def area_code_label(value: str | AreaCode | None) -> str | None:
    """Return the Korean label for a KorService2 area code."""

    if value is None:
        return None
    return AREA_CODE_LABELS.get(str(value))
