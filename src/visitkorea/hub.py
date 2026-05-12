"""Generic client for every OpenAPI service in the TourAPI Hub catalog."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator, Mapping
from typing import Any, cast

from kraddr.base import PlaceCoordinate

from ._convert import enum_value, strip_or_none, to_int_or_none, without_none
from ._http import SessionLike, TourApiHttp
from ._pagination import iter_paginated_pages
from ._provenance import call_context
from .client import DEFAULT_BASE_URL, DEFAULT_ENV_NAMES, _extract_items, _first_env
from .enums import MobileOS
from .exceptions import TourApiAuthError, TourApiRequestError
from .models import Page, RawRecord, RelatedTourItem
from .services import SERVICE_BY_KEY, SERVICE_DEFINITIONS, ServiceDefinition


class TourApiHubClient:
    """Catalog-aware client covering all services listed in useUtilExercises."""

    def __init__(
        self,
        service_key: str | None = None,
        *,
        mobile_os: MobileOS | str = MobileOS.ETC,
        mobile_app: str = "visitkorea",
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        retries: int = 3,
        session: SessionLike | None = None,
    ) -> None:
        key = service_key or _first_env(DEFAULT_ENV_NAMES)
        if not key:
            raise TourApiAuthError(
                "service_key is required. Pass service_key=... or set KTO_SERVICE_KEY."
            )
        self.service_key = key
        self.mobile_os = str(enum_value(mobile_os))
        self.mobile_app = mobile_app
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.session = session

    @classmethod
    def from_env(
        cls,
        name: str = "KTO_SERVICE_KEY",
        *,
        fallback_names: tuple[str, ...] = ("KRTOURAPI_SERVICE_KEY", "TOURAPI_SERVICE_KEY"),
        **kwargs: Any,
    ) -> TourApiHubClient:
        """Create a catalog-aware client from environment variables."""

        service_key = _first_env((name, *fallback_names))
        if not service_key:
            names = ", ".join((name, *fallback_names))
            raise TourApiAuthError(f"none of these environment variables are set: {names}")
        return cls(service_key=service_key, **kwargs)

    @property
    def services(self) -> tuple[ServiceDefinition, ...]:
        """Return the official service catalog bundled with the package."""

        return SERVICE_DEFINITIONS

    def service(self, key: str) -> TourApiServiceClient:
        """Return a service-specific generic client by key, service name, or alias."""

        try:
            definition = SERVICE_BY_KEY[key.lower()]
        except KeyError as exc:
            known = ", ".join(service.key for service in SERVICE_DEFINITIONS)
            raise TourApiRequestError(f"unknown TourAPI service {key!r}; known: {known}") from exc
        client_class = (
            RelatedTourServiceClient
            if definition.key == "related_tour"
            else TourApiServiceClient
        )
        return client_class(
            definition,
            service_key=self.service_key,
            mobile_os=self.mobile_os,
            mobile_app=self.mobile_app,
            base_url=self.base_url,
            timeout=self.timeout,
            retries=self.retries,
            session=self.session,
        )

    @property
    def related_tour(self) -> RelatedTourServiceClient:
        """Typed client for TarRlteTarService1 related-tour operations."""

        return cast(RelatedTourServiceClient, self.service("related_tour"))

    def call(
        self,
        service: str,
        operation: str,
        params: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Page[RawRecord]:
        """Call one operation from any registered service."""

        return self.service(service).call(operation, params=params, **kwargs)

    def iter_pages(
        self,
        service: str,
        operation: str,
        params: Mapping[str, Any] | None = None,
        *,
        page_no: int = 1,
        num_of_rows: int = 10,
        max_pages: int | None = None,
        max_items: int | None = None,
        **kwargs: Any,
    ) -> Iterator[Page[RawRecord]]:
        """Iterate generic Hub pages for one service operation."""

        base_params = _without_page_params(params)

        def get_page(next_page_no: int, page_size: int) -> Page[RawRecord]:
            return self.call(
                service,
                operation,
                params=base_params,
                page_no=next_page_no,
                num_of_rows=page_size,
                **kwargs,
            )

        return iter_paginated_pages(
            get_page,
            page_no=page_no,
            num_of_rows=num_of_rows,
            max_pages=max_pages,
            max_items=max_items,
        )

    def __getattr__(self, name: str) -> TourApiServiceClient:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self.service(name)
        except TourApiRequestError as exc:
            raise AttributeError(name) from exc


class TourApiServiceClient:
    """Generic operation caller for one TourAPI service."""

    def __init__(
        self,
        definition: ServiceDefinition,
        *,
        service_key: str,
        mobile_os: str,
        mobile_app: str,
        base_url: str,
        timeout: float,
        retries: int,
        session: SessionLike | None,
    ) -> None:
        self.definition = definition
        self._operation_by_alias = _operation_aliases(definition.operations)
        self._http = TourApiHttp(
            service_key,
            base_url=base_url,
            service_name=definition.service_name,
            mobile_os=mobile_os,
            mobile_app=mobile_app,
            session=session,
            timeout=timeout,
            retries=retries,
        )

    @property
    def operations(self) -> tuple[str, ...]:
        """Operations supported by this service according to the downloaded manual."""

        return self.definition.operations

    def call(
        self,
        operation: str,
        params: Mapping[str, Any] | None = None,
        *,
        page_no: int | None = 1,
        num_of_rows: int | None = 10,
        **kwargs: Any,
    ) -> Page[RawRecord]:
        """Call an operation and return normalized raw item records."""

        endpoint = self._resolve_operation(operation)
        request_params = _page_params(params={}, page_no=page_no, num_of_rows=num_of_rows)
        if params:
            request_params.update(dict(params))
        request_params.update(_pythonic_params(kwargs))
        body = self._http.get(endpoint, params=without_none(request_params))
        rows = _extract_items(body, endpoint, service_name=self.definition.service_name)
        return Page(
            items=rows,
            total_count=to_int_or_none(body.get("totalCount")) or len(rows),
            page_no=to_int_or_none(body.get("pageNo")) or page_no or 1,
            num_of_rows=to_int_or_none(body.get("numOfRows")) or num_of_rows or len(rows),
            raw=body,
            context=call_context(
                service_name=self.definition.service_name,
                endpoint=endpoint,
                mobile_os=self._http.mobile_os,
                mobile_app=self._http.mobile_app,
                params=request_params,
            ),
        )

    def iter_pages(
        self,
        operation: str,
        params: Mapping[str, Any] | None = None,
        *,
        page_no: int = 1,
        num_of_rows: int = 10,
        max_pages: int | None = None,
        max_items: int | None = None,
        **kwargs: Any,
    ) -> Iterator[Page[RawRecord]]:
        """Iterate generic pages for one operation in this service."""

        base_params = _without_page_params(params)

        def get_page(next_page_no: int, page_size: int) -> Page[RawRecord]:
            return self.call(
                operation,
                params=base_params,
                page_no=next_page_no,
                num_of_rows=page_size,
                **kwargs,
            )

        return iter_paginated_pages(
            get_page,
            page_no=page_no,
            num_of_rows=num_of_rows,
            max_pages=max_pages,
            max_items=max_items,
        )

    def __getattr__(self, name: str) -> Callable[..., Page[RawRecord]]:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            operation = self._resolve_operation(name)
        except TourApiRequestError as exc:
            raise AttributeError(name) from exc

        def caller(
            params: Mapping[str, Any] | None = None,
            *,
            page_no: int | None = 1,
            num_of_rows: int | None = 10,
            **kwargs: Any,
        ) -> Page[RawRecord]:
            return self.call(
                operation,
                params=params,
                page_no=page_no,
                num_of_rows=num_of_rows,
                **kwargs,
            )

        return caller

    def _resolve_operation(self, operation: str) -> str:
        if operation in self.definition.operations:
            return operation
        key = operation.lower()
        try:
            return self._operation_by_alias[key]
        except KeyError as exc:
            known = ", ".join(sorted(self._operation_by_alias))
            raise TourApiRequestError(
                f"{self.definition.key}: unknown operation {operation!r}; known aliases: {known}"
            ) from exc


class RelatedTourServiceClient(TourApiServiceClient):
    """Typed helper for TarRlteTarService1 related tourism records.

    `areaCd` and `signguCd` are TourAPI region codes for this service, not legal-dong
    codes. Pass them as `area_cd` and `signgu_cd` here; the request uses the official
    TourAPI parameter names.
    """

    def area_based_list(
        self,
        *,
        base_ym: str,
        area_cd: str,
        signgu_cd: str,
        page_no: int | None = 1,
        num_of_rows: int | None = 10,
        **kwargs: Any,
    ) -> Page[RelatedTourItem]:
        """Fetch related tourist attractions by TourAPI region code.

        `area_cd`/`signgu_cd` become `areaCd`/`signguCd`, which are TourAPI region
        codes for TarRlteTarService1 and not legal-dong codes.
        """

        params = {
            "baseYm": base_ym,
            "areaCd": area_cd,
            "signguCd": signgu_cd,
        }
        params.update(_pythonic_params(kwargs))
        return self._typed_related_page(
            "areaBasedList1",
            params=params,
            page_no=page_no,
            num_of_rows=num_of_rows,
        )

    def search_keyword(
        self,
        keyword: str,
        *,
        base_ym: str,
        area_cd: str,
        signgu_cd: str,
        page_no: int | None = 1,
        num_of_rows: int | None = 10,
        **kwargs: Any,
    ) -> Page[RelatedTourItem]:
        """Search related tourist attractions by keyword and TourAPI region code.

        `area_cd`/`signgu_cd` become `areaCd`/`signguCd`, which are TourAPI region
        codes for TarRlteTarService1 and not legal-dong codes.
        """

        params = {
            "baseYm": base_ym,
            "areaCd": area_cd,
            "signguCd": signgu_cd,
            "keyword": keyword,
        }
        params.update(_pythonic_params(kwargs))
        return self._typed_related_page(
            "searchKeyword1",
            params=params,
            page_no=page_no,
            num_of_rows=num_of_rows,
        )

    def iter_area_based_list(
        self,
        *,
        base_ym: str,
        area_cd: str,
        signgu_cd: str,
        page_no: int = 1,
        num_of_rows: int = 10,
        max_pages: int | None = None,
        max_items: int | None = None,
        **kwargs: Any,
    ) -> Iterator[Page[RelatedTourItem]]:
        """Iterate `area_based_list()` typed pages."""

        def get_page(next_page_no: int, page_size: int) -> Page[RelatedTourItem]:
            return self.area_based_list(
                base_ym=base_ym,
                area_cd=area_cd,
                signgu_cd=signgu_cd,
                page_no=next_page_no,
                num_of_rows=page_size,
                **kwargs,
            )

        return iter_paginated_pages(
            get_page,
            page_no=page_no,
            num_of_rows=num_of_rows,
            max_pages=max_pages,
            max_items=max_items,
        )

    def iter_search_keyword(
        self,
        keyword: str,
        *,
        base_ym: str,
        area_cd: str,
        signgu_cd: str,
        page_no: int = 1,
        num_of_rows: int = 10,
        max_pages: int | None = None,
        max_items: int | None = None,
        **kwargs: Any,
    ) -> Iterator[Page[RelatedTourItem]]:
        """Iterate `search_keyword()` typed pages."""

        def get_page(next_page_no: int, page_size: int) -> Page[RelatedTourItem]:
            return self.search_keyword(
                keyword,
                base_ym=base_ym,
                area_cd=area_cd,
                signgu_cd=signgu_cd,
                page_no=next_page_no,
                num_of_rows=page_size,
                **kwargs,
            )

        return iter_paginated_pages(
            get_page,
            page_no=page_no,
            num_of_rows=num_of_rows,
            max_pages=max_pages,
            max_items=max_items,
        )

    def _typed_related_page(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any],
        page_no: int | None,
        num_of_rows: int | None,
    ) -> Page[RelatedTourItem]:
        request_params = _page_params(params=params, page_no=page_no, num_of_rows=num_of_rows)
        body = self._http.get(endpoint, params=without_none(request_params))
        rows = _extract_items(body, endpoint, service_name=self.definition.service_name)
        parsed = tuple(_related_tour_item(row) for row in rows)
        return Page(
            items=parsed,
            total_count=to_int_or_none(body.get("totalCount")) or len(parsed),
            page_no=to_int_or_none(body.get("pageNo")) or page_no or 1,
            num_of_rows=to_int_or_none(body.get("numOfRows")) or num_of_rows or len(parsed),
            raw=body,
            context=call_context(
                service_name=self.definition.service_name,
                endpoint=endpoint,
                mobile_os=self._http.mobile_os,
                mobile_app=self._http.mobile_app,
                params=request_params,
            ),
        )


def _operation_aliases(operations: tuple[str, ...]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    counts: dict[str, int] = {}
    for operation in operations:
        snake = _snake_case(operation)
        candidates = {operation.lower(), snake}
        stripped = re.sub(r"_?\d+$", "", snake)
        if stripped != snake:
            candidates.add(stripped)
        for candidate in candidates:
            counts[candidate] = counts.get(candidate, 0) + 1
            aliases[candidate] = operation
    return {key: value for key, value in aliases.items() if counts[key] == 1}


def _snake_case(value: str) -> str:
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return value.replace("__", "_").lower()


def _page_params(
    *,
    params: Mapping[str, Any],
    page_no: int | None,
    num_of_rows: int | None,
) -> dict[str, Any]:
    request_params: dict[str, Any] = {}
    if page_no is not None:
        request_params["pageNo"] = page_no
    if num_of_rows is not None:
        request_params["numOfRows"] = num_of_rows
    request_params.update(dict(params))
    return request_params


def _without_page_params(params: Mapping[str, Any] | None) -> dict[str, Any]:
    cleaned = dict(params or {})
    cleaned.pop("pageNo", None)
    cleaned.pop("numOfRows", None)
    return cleaned


def _pythonic_params(params: Mapping[str, Any]) -> dict[str, Any]:
    converted: dict[str, Any] = {}
    for key, value in params.items():
        if key == "page_no":
            converted["pageNo"] = value
        elif key == "num_of_rows":
            converted["numOfRows"] = value
        elif key == "content_id":
            converted["contentId"] = value
        elif key == "content_type_id":
            converted["contentTypeId"] = value
        elif key == "mobile_os":
            converted["MobileOS"] = value
        elif key == "mobile_app":
            converted["MobileApp"] = value
        elif key == "coordinate":
            if isinstance(value, PlaceCoordinate):
                coordinate = value
            elif isinstance(value, tuple):
                coordinate = PlaceCoordinate.from_tuple(value)
            elif isinstance(value, Mapping):
                mapped_coordinate = PlaceCoordinate.from_mapping(value)
                if mapped_coordinate is None:
                    raise ValueError(
                        "coordinate mapping requires longitude/latitude, lon/lat, or mapX/mapY"
                    )
                coordinate = mapped_coordinate
            else:
                raise TypeError(
                    "coordinate must be PlaceCoordinate, (longitude, latitude), or mapping"
                )
            converted.update({"mapX": coordinate.lon, "mapY": coordinate.lat})
        else:
            converted[key] = value
    return converted


def _related_tour_item(row: Mapping[str, Any]) -> RelatedTourItem:
    return RelatedTourItem(
        baseYm=strip_or_none(row.get("baseYm")),
        tAtsCd=strip_or_none(row.get("tAtsCd")),
        tAtsNm=strip_or_none(row.get("tAtsNm")),
        areaCd=strip_or_none(row.get("areaCd")),
        areaNm=strip_or_none(row.get("areaNm")),
        signguCd=strip_or_none(row.get("signguCd")),
        signguNm=strip_or_none(row.get("signguNm")),
        rlteTatsCd=strip_or_none(row.get("rlteTatsCd")),
        rlteTatsNm=strip_or_none(row.get("rlteTatsNm")),
        rlteRegnCd=strip_or_none(row.get("rlteRegnCd")),
        rlteRegnNm=strip_or_none(row.get("rlteRegnNm")),
        rlteSignguCd=strip_or_none(row.get("rlteSignguCd")),
        rlteSignguNm=strip_or_none(row.get("rlteSignguNm")),
        rlteCtgryLclsNm=strip_or_none(row.get("rlteCtgryLclsNm")),
        rlteCtgryMclsNm=strip_or_none(row.get("rlteCtgryMclsNm")),
        rlteCtgrySclsNm=strip_or_none(row.get("rlteCtgrySclsNm")),
        rlteRank=strip_or_none(row.get("rlteRank")),
        raw=row,
    )
