"""Public type aliases for application integrations."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import TypeAlias

from pykrtour import PlaceCoordinate

from .enums import AreaCode, Arrange, ContentType, Language, MobileOS

ServiceKey: TypeAlias = str
AreaCodeValue: TypeAlias = str
SigunguCodeValue: TypeAlias = str
CategoryCodeValue: TypeAlias = str
LegalDongCodeValue: TypeAlias = str
ClassificationCodeValue: TypeAlias = str
ContentId: TypeAlias = str
DateInput: TypeAlias = str | date | datetime
YnInput: TypeAlias = bool | str | None
CoordinateInput: TypeAlias = PlaceCoordinate | tuple[float, float] | Mapping[str, object]
AreaCodeInput: TypeAlias = AreaCode | str | None
ContentTypeInput: TypeAlias = ContentType | str | None
ArrangeInput: TypeAlias = Arrange | str | None
MobileOSInput: TypeAlias = MobileOS | str
LanguageInput: TypeAlias = Language | str
