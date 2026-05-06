"""Dataclasses returned by the public client."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

RawRecord = Mapping[str, Any]
T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Wgs84Coordinate:
    """WGS84 longitude/latitude coordinate used by TourAPI.

    TourAPI names longitude `mapX` and latitude `mapY`. This class exposes the
    standard GIS names while keeping `map_x` and `map_y` aliases for API parity.
    """

    longitude: float
    latitude: float

    def __post_init__(self) -> None:
        longitude = float(self.longitude)
        latitude = float(self.latitude)
        if not -180 <= longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")
        if not -90 <= latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        object.__setattr__(self, "longitude", longitude)
        object.__setattr__(self, "latitude", latitude)

    @property
    def map_x(self) -> float:
        """TourAPI `mapX` value, equivalent to longitude."""

        return self.longitude

    @property
    def map_y(self) -> float:
        """TourAPI `mapY` value, equivalent to latitude."""

        return self.latitude

    @property
    def lonlat(self) -> tuple[float, float]:
        """Return `(longitude, latitude)`."""

        return (self.longitude, self.latitude)

    @property
    def latlon(self) -> tuple[float, float]:
        """Return `(latitude, longitude)` for libraries that use lat/lon order."""

        return (self.latitude, self.longitude)

    def to_tourapi_params(self) -> dict[str, float]:
        """Return TourAPI parameter names for this coordinate."""

        return {"mapX": self.longitude, "mapY": self.latitude}


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    """A paginated TourAPI response."""

    items: tuple[T, ...]
    total_count: int
    page_no: int
    num_of_rows: int
    raw: RawRecord = field(repr=False)

    @property
    def is_empty(self) -> bool:
        return not self.items


@dataclass(frozen=True, slots=True)
class TourItem:
    """Common list/search item from TourAPI."""

    content_id: str | None
    content_type_id: str | None
    title: str | None
    addr1: str | None
    addr2: str | None
    area_code: str | None
    sigungu_code: str | None
    cat1: str | None
    cat2: str | None
    cat3: str | None
    l_dong_regn_cd: str | None
    l_dong_signgu_cd: str | None
    lcls_systm1: str | None
    lcls_systm2: str | None
    lcls_systm3: str | None
    created_time: datetime | None
    modified_time: datetime | None
    tel: str | None
    first_image: str | None
    first_image2: str | None
    map_x: float | None
    map_y: float | None
    map_level: str | None
    distance_m: float | None
    zipcode: str | None
    copyright_division_code: str | None
    show_flag: str | None
    raw: RawRecord = field(repr=False)

    @property
    def coordinate(self) -> Wgs84Coordinate | None:
        """Return standardized WGS84 coordinates when both axes are present."""

        if self.map_x is None or self.map_y is None:
            return None
        return Wgs84Coordinate(longitude=self.map_x, latitude=self.map_y)


@dataclass(frozen=True, slots=True)
class TourDetail:
    """Common detail information for one content item."""

    content_id: str | None
    content_type_id: str | None
    title: str | None
    homepage: str | None
    overview: str | None
    tel: str | None
    tel_name: str | None
    addr1: str | None
    addr2: str | None
    zipcode: str | None
    area_code: str | None
    sigungu_code: str | None
    cat1: str | None
    cat2: str | None
    cat3: str | None
    l_dong_regn_cd: str | None
    l_dong_signgu_cd: str | None
    lcls_systm1: str | None
    lcls_systm2: str | None
    lcls_systm3: str | None
    first_image: str | None
    first_image2: str | None
    map_x: float | None
    map_y: float | None
    map_level: str | None
    created_time: datetime | None
    modified_time: datetime | None
    copyright_division_code: str | None
    raw: RawRecord = field(repr=False)

    @property
    def coordinate(self) -> Wgs84Coordinate | None:
        """Return standardized WGS84 coordinates when both axes are present."""

        if self.map_x is None or self.map_y is None:
            return None
        return Wgs84Coordinate(longitude=self.map_x, latitude=self.map_y)


@dataclass(frozen=True, slots=True)
class CodeItem:
    """Code lookup item for area, category, legal dong, or classification codes."""

    code: str | None
    name: str | None
    rnum: int | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True, slots=True)
class IntroInfo:
    """Introduction detail record. The field set depends on content_type_id."""

    content_id: str | None
    content_type_id: str | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True, slots=True)
class RepeatInfo:
    """Repeated detail record such as course stops or facility sub-items."""

    content_id: str | None
    content_type_id: str | None
    serial_num: str | None
    info_name: str | None
    info_text: str | None
    field_group: str | None
    sub_name: str | None
    sub_detail_overview: str | None
    sub_detail_img: str | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True, slots=True)
class ImageInfo:
    """Image metadata returned by detailImage2."""

    content_id: str | None
    serial_num: str | None
    image_name: str | None
    origin_img_url: str | None
    small_image_url: str | None
    copyright_division_code: str | None
    raw: RawRecord = field(repr=False)
