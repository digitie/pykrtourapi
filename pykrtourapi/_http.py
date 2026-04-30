"""HTTP helpers and TourAPI envelope/error mapping."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, cast
from xml.etree import ElementTree

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ._convert import without_none
from .exceptions import (
    TourApiAuthError,
    TourApiParseError,
    TourApiRateLimitError,
    TourApiRequestError,
    TourApiServerError,
)


class ResponseLike(Protocol):
    status_code: int
    text: str

    def json(self) -> Any: ...


class SessionLike(Protocol):
    def get(self, url: str, *, params: Mapping[str, Any], timeout: float) -> ResponseLike: ...


TRANSIENT_STATUSES = {429, 500, 502, 503, 504}
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; pykrtourapi/0.1; "
    "+https://github.com/digitie/pykrtourapi)"
)


def build_session(retries: int = 3) -> SessionLike:
    """Build a requests session with conservative GET retries."""

    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
    if retries <= 0:
        return cast(SessionLike, session)

    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=0.3,
        status_forcelist=tuple(sorted(TRANSIENT_STATUSES)),
        allowed_methods=frozenset({"GET"}),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return cast(SessionLike, session)


class TourApiHttp:
    """Low-level JSON client for the data.go.kr TourAPI envelope."""

    def __init__(
        self,
        service_key: str,
        *,
        base_url: str,
        service_name: str,
        mobile_os: str,
        mobile_app: str,
        session: SessionLike | None = None,
        timeout: float = 10.0,
        retries: int = 3,
    ) -> None:
        if not service_key:
            raise TourApiAuthError("service_key is required")
        self.service_key = service_key
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name.strip("/")
        self.mobile_os = mobile_os
        self.mobile_app = mobile_app
        self.session = session or build_session(retries)
        self.timeout = timeout

    def get(self, endpoint: str, params: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        endpoint_path = endpoint.strip("/")
        url = f"{self.base_url}/{self.service_name}/{endpoint_path}"
        request_params: dict[str, Any] = {
            "serviceKey": self.service_key,
            "MobileOS": self.mobile_os,
            "MobileApp": self.mobile_app,
            "_type": "json",
        }
        if params:
            request_params.update(dict(params))

        response = self.session.get(url, params=without_none(request_params), timeout=self.timeout)
        _raise_for_status(response)
        try:
            payload = response.json()
        except ValueError as exc:
            _raise_for_xml_error(response.text)
            raise TourApiParseError(f"TourAPI response was not valid JSON: {exc}") from exc
        return _extract_body(payload)


def _raise_for_status(response: ResponseLike) -> None:
    status = response.status_code
    text = response.text[:300]
    if status in {401, 403}:
        raise TourApiAuthError(f"HTTP {status}: {text}")
    if status == 429:
        raise TourApiRateLimitError(f"HTTP {status}: {text}")
    if 400 <= status < 500:
        raise TourApiRequestError(f"HTTP {status}: {text}")
    if 500 <= status < 600:
        raise TourApiServerError(f"HTTP {status}: {text}")


def _extract_body(payload: Any) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise TourApiParseError("TourAPI JSON root was not an object")

    if "OpenAPI_ServiceResponse" in payload:
        _raise_for_data_error(payload["OpenAPI_ServiceResponse"])

    try:
        response = payload["response"]
        header = response["header"]
    except (KeyError, TypeError) as exc:
        raise TourApiParseError("TourAPI response did not contain response.header") from exc

    if not isinstance(response, Mapping) or not isinstance(header, Mapping):
        raise TourApiParseError("TourAPI response/header was not an object")

    code = str(header.get("resultCode", "")).strip()
    message = str(header.get("resultMsg", "")).strip()
    body = response.get("body", {})
    if code in {"00", "0000", "0", "NORMAL_CODE", ""}:
        if not isinstance(body, Mapping):
            raise TourApiParseError("TourAPI response.body was not an object")
        return body
    if code == "03":
        return body if isinstance(body, Mapping) else {}
    _raise_for_result_code(code, message)
    raise AssertionError("unreachable")


def _raise_for_xml_error(text: str) -> None:
    text = text.strip()
    if not text.startswith("<"):
        return
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError:
        return

    values: dict[str, str] = {}
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if element.text and element.text.strip():
            values[tag] = element.text.strip()

    code = values.get("returnReasonCode", "")
    message = (
        values.get("returnAuthMsg")
        or values.get("errMsg")
        or values.get("resultMsg")
        or "TourAPI XML error response"
    )
    _raise_for_result_code(code, message)


def _raise_for_data_error(data: Any) -> None:
    if not isinstance(data, Mapping):
        raise TourApiParseError("OpenAPI_ServiceResponse was not an object")
    header = data.get("cmmMsgHeader", data)
    if not isinstance(header, Mapping):
        raise TourApiParseError("OpenAPI_ServiceResponse header was not an object")
    code = str(header.get("returnReasonCode", "")).strip()
    message = str(
        header.get("returnAuthMsg")
        or header.get("errMsg")
        or header.get("resultMsg")
        or "TourAPI service error"
    )
    _raise_for_result_code(code, message)


def _raise_for_result_code(code: str, message: str) -> None:
    text = f"TourAPI returned {code}: {message}" if code else message
    upper = text.upper()
    if code in {"20", "30", "31"} or "SERVICE_KEY" in upper or "AUTH" in upper:
        raise TourApiAuthError(text)
    if code in {"22"} or "LIMIT" in upper or "QUOTA" in upper or "TRAFFIC" in upper:
        raise TourApiRateLimitError(text)
    if code in {"04", "99"} or code.startswith("5"):
        raise TourApiServerError(text)
    raise TourApiRequestError(text)
