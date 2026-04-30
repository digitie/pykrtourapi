from __future__ import annotations

import pytest

from pykrtourapi._http import DEFAULT_USER_AGENT, TourApiHttp, build_session
from pykrtourapi.enums import MobileOS
from pykrtourapi.exceptions import (
    TourApiAuthError,
    TourApiParseError,
    TourApiRateLimitError,
    TourApiRequestError,
    TourApiServerError,
)

from .conftest import FakeResponse, tour_payload


def test_common_request_params_and_endpoint_url(fake_client_factory):
    client, session = fake_client_factory(
        FakeResponse(tour_payload([])),
        mobile_app="UnitTest",
        mobile_os=MobileOS.WEB,
    )

    page = client.area_codes()

    assert page.items == ()
    call = session.calls[0]
    assert call["url"] == "http://apis.data.go.kr/B551011/KorService2/areaCode2"
    assert call["params"]["serviceKey"] == "TEST_KEY"
    assert call["params"]["MobileOS"] == "WEB"
    assert call["params"]["MobileApp"] == "UnitTest"
    assert call["params"]["_type"] == "json"
    assert call["params"]["pageNo"] == 1
    assert "areaCode" not in call["params"]


def test_non_json_xml_service_key_error_maps_to_auth(fake_client_factory):
    xml = """
    <OpenAPI_ServiceResponse>
      <cmmMsgHeader>
        <errMsg>SERVICE ERROR</errMsg>
        <returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg>
        <returnReasonCode>30</returnReasonCode>
      </cmmMsgHeader>
    </OpenAPI_ServiceResponse>
    """
    client, _session = fake_client_factory(
        FakeResponse(text=xml, json_error=ValueError("not json")),
    )

    with pytest.raises(TourApiAuthError, match="SERVICE_KEY_IS_NOT_REGISTERED_ERROR"):
        client.area_codes()


def test_result_code_03_returns_empty_page(fake_client_factory):
    client, _session = fake_client_factory(
        FakeResponse(tour_payload(None, result_code="03", result_msg="NO_DATA")),
    )

    page = client.area_codes()

    assert page.is_empty
    assert page.total_count == 0


def test_result_code_0000_is_treated_as_success(fake_client_factory):
    client, _session = fake_client_factory(
        FakeResponse(tour_payload([], result_code="0000", result_msg="OK")),
    )

    page = client.area_codes()

    assert page.items == ()


def test_http_and_header_error_mapping(fake_client_factory):
    client, _session = fake_client_factory(FakeResponse({}, status_code=429, text="too many"))
    with pytest.raises(TourApiRateLimitError):
        client.area_codes()

    client, _session = fake_client_factory(
        FakeResponse(
            {
                "response": {
                    "header": {"resultCode": "99", "resultMsg": "SERVER_ERROR"},
                    "body": {},
                }
            }
        )
    )
    with pytest.raises(TourApiServerError):
        client.area_codes()


def test_malformed_items_shape_raises_parse_error(fake_client_factory):
    payload = tour_payload("not-a-dict")
    client, _session = fake_client_factory(FakeResponse(payload))

    with pytest.raises(TourApiParseError):
        client.area_codes()


def test_build_session_and_empty_service_key():
    session = build_session(retries=0)
    assert session is not None
    assert session.headers["User-Agent"] == DEFAULT_USER_AGENT
    assert build_session(retries=1) is not None

    with pytest.raises(TourApiAuthError):
        TourApiHttp(
            "",
            base_url="http://example.com",
            service_name="KorService2",
            mobile_os="ETC",
            mobile_app="test",
        )


def test_more_http_error_branches(fake_client_factory):
    client, _session = fake_client_factory(FakeResponse("not-object"))
    with pytest.raises(TourApiParseError, match="root"):
        client.area_codes()

    client, _session = fake_client_factory(FakeResponse({"response": {}}))
    with pytest.raises(TourApiParseError, match="response.header"):
        client.area_codes()

    client, _session = fake_client_factory(
        FakeResponse({"response": {"header": {"resultCode": "00"}, "body": []}})
    )
    with pytest.raises(TourApiParseError, match="body"):
        client.area_codes()

    client, _session = fake_client_factory(FakeResponse({}, status_code=401, text="denied"))
    with pytest.raises(TourApiAuthError):
        client.area_codes()

    client, _session = fake_client_factory(FakeResponse({}, status_code=400, text="bad"))
    with pytest.raises(TourApiRequestError):
        client.area_codes()

    client, _session = fake_client_factory(FakeResponse({}, status_code=500, text="down"))
    with pytest.raises(TourApiServerError):
        client.area_codes()


def test_non_xml_json_parse_error_stays_parse_error(fake_client_factory):
    client, _session = fake_client_factory(
        FakeResponse(text="not xml", json_error=ValueError("bad json")),
    )

    with pytest.raises(TourApiParseError, match="not valid JSON"):
        client.area_codes()


def test_json_openapi_service_response_errors(fake_client_factory):
    client, _session = fake_client_factory(
        FakeResponse(
            {
                "OpenAPI_ServiceResponse": {
                    "cmmMsgHeader": {
                        "returnReasonCode": "22",
                        "returnAuthMsg": "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR",
                    }
                }
            }
        )
    )
    with pytest.raises(TourApiRateLimitError):
        client.area_codes()

    client, _session = fake_client_factory(FakeResponse({"OpenAPI_ServiceResponse": []}))
    with pytest.raises(TourApiParseError):
        client.area_codes()
