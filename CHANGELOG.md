# Changelog

## 0.1.0

- Initial `pykrtourapi` package scaffold.
- Added `KrTourApiClient` for Korea Tourism Organization TourAPI `KorService2`.
- Added list/search/detail/image/sync/code lookup methods.
- Added typed dataclass models and exception hierarchy.
- Added offline tests for request shape, response parsing, error mapping, validation, and CLI output.
- Added README, API notes, testing guide, troubleshooting guide, and repeated mistake guardrails.
- Added `TourApiHubClient` and `SERVICE_DEFINITIONS` for all 27 OpenAPI services listed on `api.visitkorea.or.kr/#/useUtilExercises`.
- Added `docs/openapi-catalog.md` and a manual download script for reproducing the official ZIP/DOCX review.
- Added offline tests for Hub service routing, operation aliases, environment fallback, and Pythonic parameter aliases.
