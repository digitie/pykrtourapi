from __future__ import annotations

from datetime import date

import pytest

from pykrtourapi import Wgs84Coordinate
from pykrtourapi.client import KrTourApiClient
from pykrtourapi.enums import AreaCode, Arrange, ContentType, Language
from pykrtourapi.exceptions import TourApiAuthError, TourApiNoDataError, TourApiRequestError

from .conftest import FakeResponse, FakeSession, tour_payload


def sample_tour_item() -> dict[str, str]:
    return {
        "contentid": "126508",
        "contenttypeid": "12",
        "title": "경복궁",
        "addr1": "서울특별시 종로구 사직로 161",
        "addr2": "",
        "areacode": "1",
        "sigungucode": "23",
        "cat1": "A02",
        "cat2": "A0201",
        "cat3": "A02010100",
        "lDongRegnCd": "11",
        "lDongSignguCd": "110",
        "lclsSystm1": "HS",
        "lclsSystm2": "HS01",
        "lclsSystm3": "HS010100",
        "createdtime": "20240101112233",
        "modifiedtime": "20240102112233",
        "tel": "02-3700-3900",
        "firstimage": "https://example.com/main.jpg",
        "firstimage2": "https://example.com/thumb.jpg",
        "mapx": "126.9769",
        "mapy": "37.5796",
        "mlevel": "6",
        "dist": "125.4",
        "zipcode": "03045",
        "cpyrhtDivCd": "Type1",
        "showFlag": "1",
    }


def test_search_keyword_sends_filters_and_parses_item(fake_client_factory):
    client, session = fake_client_factory(FakeResponse(tour_payload(sample_tour_item())))

    page = client.search_keyword(
        "궁",
        content_type_id=ContentType.TOURIST_ATTRACTION,
        l_dong_regn_cd="11",
        l_dong_signgu_cd="110",
        lcls_systm1="HS",
        arrange=Arrange.MODIFIED_WITH_IMAGE,
    )

    call = session.calls[0]
    assert call["url"].endswith("/KorService2/searchKeyword2")
    assert call["params"]["keyword"] == "궁"
    assert call["params"]["contentTypeId"] == "12"
    assert call["params"]["lDongRegnCd"] == "11"
    assert call["params"]["lDongSignguCd"] == "110"
    assert call["params"]["arrange"] == "Q"

    item = page.items[0]
    assert item.content_id == "126508"
    assert item.title == "경복궁"
    assert item.addr2 is None
    assert item.map_x == 126.9769
    assert item.map_y == 37.5796
    assert item.coordinate == Wgs84Coordinate(longitude=126.9769, latitude=37.5796)
    assert item.distance_m == 125.4
    assert item.created_time is not None
    assert item.created_time.year == 2024
    assert item.show_flag == "1"


def test_festival_dates_are_normalized(fake_client_factory):
    client, session = fake_client_factory(FakeResponse(tour_payload([])))

    client.search_festival(
        date(2026, 4, 30),
        event_end_date="20260501",
        modified_time=date(2026, 4, 1),
    )

    params = session.calls[0]["params"]
    assert session.calls[0]["url"].endswith("/searchFestival2")
    assert params["eventStartDate"] == "20260430"
    assert params["eventEndDate"] == "20260501"
    assert params["modifiedtime"] == "20260401"


def test_area_location_and_stay_endpoints(fake_client_factory):
    client, session = fake_client_factory(
        FakeResponse(tour_payload([])),
        FakeResponse(tour_payload([])),
        FakeResponse(tour_payload([])),
    )

    client.area_based_list(area_code=AreaCode.SEOUL, num_of_rows=5)
    client.location_based_list(map_x=126.9, map_y=37.5, radius=500)
    client.search_stay(area_code=AreaCode.SEOUL)

    assert session.calls[0]["url"].endswith("/areaBasedList2")
    assert session.calls[0]["params"]["areaCode"] == "1"
    assert session.calls[0]["params"]["numOfRows"] == 5
    assert session.calls[1]["url"].endswith("/locationBasedList2")
    assert session.calls[1]["params"]["mapX"] == 126.9
    assert session.calls[1]["params"]["radius"] == 500
    assert session.calls[2]["url"].endswith("/searchStay2")


def test_location_radius_validation(fake_client_factory):
    client, _session = fake_client_factory(FakeResponse(tour_payload([])))

    with pytest.raises(ValueError, match="radius"):
        client.location_based_list(map_x=126.9, map_y=37.5, radius=20001)
    with pytest.raises(ValueError, match="coordinate"):
        client.location_based_list(radius=100)
    with pytest.raises(ValueError, match="cannot be combined"):
        client.location_based_list(
            coordinate=Wgs84Coordinate(longitude=126.9, latitude=37.5),
            map_x=126.9,
            radius=100,
        )


def test_location_accepts_standard_coordinate_inputs(fake_client_factory):
    client, session = fake_client_factory(
        FakeResponse(tour_payload([])),
        FakeResponse(tour_payload([])),
        FakeResponse(tour_payload([])),
    )

    client.location_based_list(
        coordinate=Wgs84Coordinate(longitude=126.9769, latitude=37.5796),
        radius=1000,
    )
    client.location_based_list(coordinate=(127.0, 37.5), radius=1000)
    client.location_based_list(coordinate={"longitude": 127.1, "latitude": 37.6}, radius=1000)

    assert session.calls[0]["params"]["mapX"] == 126.9769
    assert session.calls[0]["params"]["mapY"] == 37.5796
    assert session.calls[1]["params"]["mapX"] == 127.0
    assert session.calls[2]["params"]["mapY"] == 37.6


def test_more_client_validation(fake_client_factory):
    client, _session = fake_client_factory(FakeResponse(tour_payload([])))

    with pytest.raises(ValueError, match="keyword"):
        client.search_keyword(" ")
    with pytest.raises(ValueError, match="content_id"):
        client.detail_common("")
    with pytest.raises(ValueError, match="content_id"):
        client.detail_images("")
    with pytest.raises(ValueError, match="show_flag"):
        client.area_based_sync_list(show_flag="Y")
    with pytest.raises(ValueError, match="page_no"):
        client.area_codes(page_no=0)
    with pytest.raises(ValueError, match="num_of_rows"):
        client.area_codes(num_of_rows=1001)
    with pytest.raises(TourApiRequestError, match="cat2"):
        client.category_codes(cat2="A0201")
    with pytest.raises(TourApiRequestError, match="lcls_systm3"):
        client.classification_system_codes(lcls_systm1="HS", lcls_systm3="HS010100")
    with pytest.raises(ValueError, match="content_id"):
        client.detail_intro("", "12")


def test_dependent_filter_validation(fake_client_factory):
    client, _session = fake_client_factory(FakeResponse(tour_payload([])))

    with pytest.raises(TourApiRequestError, match="sigungu_code"):
        client.area_based_list(sigungu_code="23")
    with pytest.raises(TourApiRequestError, match="cat3"):
        client.area_based_list(cat1="A02", cat3="A02010100")
    with pytest.raises(TourApiRequestError, match="l_dong_signgu_cd"):
        client.area_based_list(l_dong_signgu_cd="110")
    with pytest.raises(TourApiRequestError, match="lcls_systm2"):
        client.area_based_list(lcls_systm2="HS01")


def test_detail_common_raises_no_data_for_empty_detail(fake_client_factory):
    client, _session = fake_client_factory(
        FakeResponse(tour_payload(None, result_code="03", result_msg="NO_DATA")),
    )

    with pytest.raises(TourApiNoDataError):
        client.detail_common("missing")


def test_detail_common_parses_detail(fake_client_factory):
    row = sample_tour_item() | {
        "homepage": "<a href='https://example.com'>홈</a>",
        "overview": "설명",
    }
    client, _session = fake_client_factory(FakeResponse(tour_payload(row)))

    detail = client.detail_common("126508")

    assert detail.content_id == "126508"
    assert detail.homepage is not None
    assert detail.overview == "설명"
    assert detail.copyright_division_code == "Type1"


def test_detail_intro_info_and_images(fake_client_factory):
    intro = {"contentid": "1", "contenttypeid": "12", "infocenter": "안내"}
    repeat = {
        "contentid": "1",
        "contenttypeid": "25",
        "serialnum": "0",
        "infoname": "코스",
        "infotext": "본문",
        "fldgubun": "1",
    }
    image = {
        "contentid": "1",
        "serialnum": "1",
        "imgname": "대표",
        "originimgurl": "https://example.com/origin.jpg",
        "smallimageurl": "https://example.com/small.jpg",
        "cpyrhtDivCd": "Type3",
    }
    client, session = fake_client_factory(
        FakeResponse(tour_payload(intro)),
        FakeResponse(tour_payload(repeat)),
        FakeResponse(tour_payload(image)),
    )

    intro_page = client.detail_intro("1", ContentType.TOURIST_ATTRACTION)
    repeat_page = client.detail_info("1", "25")
    image_page = client.detail_images("1", image_yn=True, sub_image_yn=False)

    assert intro_page.items[0].raw["infocenter"] == "안내"
    assert repeat_page.items[0].info_name == "코스"
    assert image_page.items[0].origin_img_url == "https://example.com/origin.jpg"
    assert session.calls[2]["params"]["imageYN"] == "Y"
    assert session.calls[2]["params"]["subImageYN"] == "N"


def test_sync_and_code_endpoints(fake_client_factory):
    client, session = fake_client_factory(
        FakeResponse(tour_payload(sample_tour_item())),
        FakeResponse(tour_payload({"code": "1", "name": "서울", "rnum": "1"})),
        FakeResponse(tour_payload({"lDongRegnCd": "11", "lDongRegnNm": "서울특별시"})),
        FakeResponse(tour_payload({"lclsSystm1Cd": "HS", "lclsSystm1Nm": "역사관광"})),
    )

    sync_page = client.area_based_sync_list(show_flag="1", area_code="1", sigungu_code="23")
    area_page = client.area_codes()
    legal_page = client.legal_dong_codes(list_yn=True)
    lcls_page = client.classification_system_codes(list_yn=True)

    assert sync_page.items[0].show_flag == "1"
    assert session.calls[0]["params"]["showFlag"] == "1"
    assert area_page.items[0].code == "1"
    assert legal_page.items[0].code == "11"
    assert lcls_page.items[0].name == "역사관광"


def test_raw_endpoint_preserves_raw_records(fake_client_factory):
    rows = [{"custom": "value"}, {"custom": "value2"}]
    client, session = fake_client_factory(FakeResponse(tour_payload(rows)))

    page = client.raw_endpoint("customEndpoint2", {"foo": "bar"})

    assert page.items[0]["custom"] == "value"
    assert page.items[1]["custom"] == "value2"
    assert session.calls[0]["url"].endswith("/customEndpoint2")
    assert session.calls[0]["params"]["foo"] == "bar"


def test_env_and_language_errors(monkeypatch, fake_client_factory):
    monkeypatch.delenv("KTO_SERVICE_KEY", raising=False)
    monkeypatch.delenv("KRTOURAPI_SERVICE_KEY", raising=False)
    monkeypatch.delenv("TOURAPI_SERVICE_KEY", raising=False)

    with pytest.raises(TourApiAuthError):
        KrTourApiClient()
    with pytest.raises(TourApiAuthError):
        KrTourApiClient.from_env()
    with pytest.raises(ValueError, match="unsupported language"):
        KrTourApiClient("KEY", language="xx")
    language_client = KrTourApiClient("KEY", language=Language.KOREAN, session=FakeSession([]))
    assert language_client.service_name == "KorService2"

    monkeypatch.setenv("KTO_SERVICE_KEY", "ENV_KEY")
    client, session = fake_client_factory(FakeResponse(tour_payload([])))
    env_client = KrTourApiClient(session=session)
    env_client.area_codes()
    assert client.service_key == "TEST_KEY"
    assert session.calls[0]["params"]["serviceKey"] == "ENV_KEY"
