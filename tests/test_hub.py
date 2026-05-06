from __future__ import annotations

import pytest

from pykrtourapi import SERVICE_DEFINITIONS, TourApiHubClient, Wgs84Coordinate
from pykrtourapi.exceptions import TourApiRequestError

from .conftest import FakeResponse, FakeSession, tour_payload

EXPECTED_SERVICE_KEYS = {
    "area_demand_strength",
    "area_diversity",
    "area_resource_demand",
    "chs",
    "cht",
    "datalab",
    "durunubi",
    "employment",
    "eng",
    "fre",
    "ger",
    "gocamping",
    "green",
    "jpn",
    "kor",
    "local_hub",
    "medical",
    "odii",
    "pet",
    "photo_award",
    "photo_gallery",
    "related_tour",
    "rus",
    "spn",
    "tats_concentration",
    "wellness",
    "with",
}


def test_catalog_contains_all_manual_services():
    keys = {service.key for service in SERVICE_DEFINITIONS}

    assert len(SERVICE_DEFINITIONS) == 27
    assert keys == EXPECTED_SERVICE_KEYS
    assert sum(len(service.operations) for service in SERVICE_DEFINITIONS) == 211
    assert all(
        service.manual_url.startswith("https://api.visitkorea.or.kr/")
        for service in SERVICE_DEFINITIONS
    )


def test_all_catalog_operations_are_routable_without_live_api_calls():
    total_operations = sum(len(service.operations) for service in SERVICE_DEFINITIONS)
    session = FakeSession([FakeResponse(tour_payload(None)) for _ in range(total_operations)])
    hub = TourApiHubClient("KEY", session=session)

    for service in SERVICE_DEFINITIONS:
        service_client = hub.service(service.key)
        for operation in service.operations:
            page = service_client.call(operation, page_no=None, num_of_rows=None)

            assert page.items == ()
            call = session.calls[-1]
            assert call["url"].endswith(f"/{service.service_name}/{operation}")
            assert call["params"]["serviceKey"] == "KEY"
            assert call["params"]["MobileOS"] == "ETC"
            assert call["params"]["MobileApp"] == "pykrtourapi"
            assert call["params"]["_type"] == "json"

    assert len(session.calls) == total_operations


def test_hub_from_env_uses_fallback_names(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KTO_SERVICE_KEY", raising=False)
    monkeypatch.setenv("TOURAPI_SERVICE_KEY", "ENVKEY")

    hub = TourApiHubClient.from_env(session=FakeSession([]))

    assert hub.service_key == "ENVKEY"


def test_hub_call_by_service_key_and_operation_alias():
    session = FakeSession([FakeResponse(tour_payload({"contentid": "1", "title": "캠핑"}))])
    hub = TourApiHubClient("KEY", session=session)

    page = hub.call("gocamping", "based_list", facltNm="숲")

    assert page.items[0]["title"] == "캠핑"
    call = session.calls[0]
    assert call["url"] == "http://apis.data.go.kr/B551011/GoCamping/basedList"
    assert call["params"]["serviceKey"] == "KEY"
    assert call["params"]["facltNm"] == "숲"
    assert call["params"]["pageNo"] == 1
    assert call["params"]["numOfRows"] == 10


def test_hub_dynamic_service_and_operation_methods():
    session = FakeSession([FakeResponse(tour_payload({"galContentId": "A"}))])
    hub = TourApiHubClient("KEY", session=session)

    page = hub.photo.gallery_list(page_no=2, num_of_rows=3, galSearchKeyword="서울")

    assert page.page_no == 1
    assert page.items[0]["galContentId"] == "A"
    assert session.calls[0]["url"].endswith("/PhotoGalleryService1/galleryList1")
    assert session.calls[0]["params"]["pageNo"] == 2
    assert session.calls[0]["params"]["numOfRows"] == 3


def test_hub_pythonic_param_aliases():
    session = FakeSession([FakeResponse(tour_payload({"contentid": "1"}))])
    hub = TourApiHubClient("KEY", session=session)

    hub.kor.detail_common(content_id="1", content_type_id="12")

    params = session.calls[0]["params"]
    assert session.calls[0]["url"].endswith("/KorService2/detailCommon2")
    assert params["contentId"] == "1"
    assert params["contentTypeId"] == "12"


def test_hub_coordinate_alias_expands_to_tourapi_params():
    session = FakeSession([FakeResponse(tour_payload({"contentid": "1"}))])
    hub = TourApiHubClient("KEY", session=session)

    hub.kor.location_based_list(
        coordinate=Wgs84Coordinate(longitude=126.9769, latitude=37.5796),
        radius=1000,
    )

    params = session.calls[0]["params"]
    assert params["mapX"] == 126.9769
    assert params["mapY"] == 37.5796
    assert params["radius"] == 1000


def test_hub_unknown_service_and_operation_errors():
    hub = TourApiHubClient("KEY", session=FakeSession([]))

    with pytest.raises(TourApiRequestError, match="unknown TourAPI service"):
        hub.service("missing")
    with pytest.raises(TourApiRequestError, match="unknown operation"):
        hub.service("kor").call("missing")
    with pytest.raises(AttributeError):
        _ = hub.missing
    with pytest.raises(AttributeError):
        _ = hub.kor.missing
