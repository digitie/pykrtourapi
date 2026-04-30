"""Exception hierarchy for pykrtourapi."""

from __future__ import annotations


class TourApiError(Exception):
    """Base exception for all pykrtourapi errors."""


class TourApiAuthError(TourApiError):
    """Authentication or service-key failure."""


class TourApiRateLimitError(TourApiError):
    """API quota or traffic limit failure."""


class TourApiRequestError(TourApiError):
    """Invalid request, unsupported parameter, or non-retryable 4xx failure."""


class TourApiNoDataError(TourApiError):
    """A detail endpoint returned no item where one item was expected."""


class TourApiServerError(TourApiError):
    """TourAPI server-side failure."""


class TourApiParseError(TourApiError):
    """Response shape or type conversion failure."""
