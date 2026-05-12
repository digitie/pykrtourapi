from __future__ import annotations

from visitkorea import AreaCode, Arrange, ContentType, CoordinateInput, Language, MobileOS
from visitkorea.client import KrTourApiClient
from visitkorea.enums import area_code_label, content_type_label

from .conftest import FakeResponse, tour_payload


def test_content_type_labels():
    assert content_type_label(ContentType.TOURIST_ATTRACTION) == "관광지"
    assert content_type_label("39") == "음식점"
    assert content_type_label("999") is None
    assert area_code_label(AreaCode.SEOUL) == "서울"
    assert area_code_label("39") == "제주"
    assert area_code_label("999") is None


def test_language_maps_to_service_name():
    session_response = FakeResponse(tour_payload([]))
    from .conftest import FakeSession

    session = FakeSession([session_response])
    client = KrTourApiClient(
        "KEY",
        language=Language.ENGLISH,
        session=session,
        mobile_os=MobileOS.ETC,
    )
    client.area_codes()

    assert session.calls[0]["url"].endswith("/EngService2/areaCode2")
    assert str(Arrange.TITLE) == "A"
    assert CoordinateInput is not None
