"""Helpers for response call provenance."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from ._http import public_request_params
from ._time import KST
from .models import TourApiCallContext


def call_context(
    *,
    service_name: str,
    endpoint: str,
    mobile_os: str,
    mobile_app: str,
    params: Mapping[str, Any],
) -> TourApiCallContext:
    """Build safe response metadata for a TourAPI call."""

    return TourApiCallContext(
        service_name=service_name,
        endpoint=endpoint,
        request_params=public_request_params(
            mobile_os=mobile_os,
            mobile_app=mobile_app,
            params=params,
        ),
        collected_at=datetime.now(tz=KST),
    )
