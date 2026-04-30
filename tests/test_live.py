from __future__ import annotations

import os

import pytest

from pykrtourapi import KrTourApiClient, TourApiHubClient
from pykrtourapi.exceptions import TourApiAuthError

pytestmark = pytest.mark.live


def _service_key() -> str:
    key = os.getenv("KTO_SERVICE_KEY")
    if not key:
        pytest.skip("KTO_SERVICE_KEY is not set")
    return key


def test_live_korean_area_codes_returns_tourapi_shape():
    client = KrTourApiClient(
        _service_key(),
        mobile_app="pykrtourapi-live-test",
        timeout=20,
    )

    page = client.area_codes(num_of_rows=5)

    assert page.page_no >= 1
    assert page.num_of_rows >= 1
    assert page.total_count >= len(page.items)
    assert isinstance(page.raw, dict)
    for item in page.items:
        assert item.raw


def test_live_unsubscribed_foreign_service_maps_to_auth_error():
    hub = TourApiHubClient(
        _service_key(),
        mobile_app="pykrtourapi-live-test",
        timeout=20,
    )

    with pytest.raises(TourApiAuthError, match="403|SERVICE|AUTH|KEY|SERVICE_KEY"):
        hub.eng.area_code(num_of_rows=1)
