# Agent Notes

This repository is a small typed Python package. Keep changes narrow, tested, and documented.

## Before editing public behavior

1. Read `README.md`.
2. Read `krtourapi-api.md`.
3. Check `docs/repeated-mistakes.md`.
4. Add or update offline tests first when the behavior is easy to fixture.

## Module ownership

```text
pykrtourapi/
├── client.py       # public client methods and response parsing
├── hub.py          # catalog-aware generic client for all official TourAPI services
├── services.py     # downloaded manual catalog distilled into service definitions
├── _http.py        # requests session, TourAPI envelope, error mapping
├── _convert.py     # small conversion helpers
├── _time.py        # KST timestamp parsing
├── enums.py        # public constants and enum values
├── models.py       # public Pydantic response models
├── types.py        # public type aliases for downstream integrations
├── exceptions.py   # public exception hierarchy
└── cli.py          # command-line entrypoint
```

## Test policy

- Ordinary tests must be offline.
- Use fake sessions or `responses` for HTTP behavior.
- Live tests require `@pytest.mark.live` and `KTO_SERVICE_KEY`.
- Do not assert unstable real tourism data values in live tests; assert shape and types only.
- Keep `TourApiHubClient` tests catalog-driven; do not call the real 27 services in default tests.
- Keep official manual ZIP/DOCX downloads in `.manuals/`, never in git.
- Keep coordinate tests explicit about `PlaceCoordinate` WGS84 `lon`/`lat` and TourAPI `mapX`/`mapY`.

## Verification commands

```bash
python -m compileall pykrtourapi tests
python -m pytest
python -m pytest --cov=pykrtourapi --cov-fail-under=90
ruff check .
mypy pykrtourapi
```

## Documentation policy

When a mistake is fixed, update `docs/repeated-mistakes.md` with:

- symptom
- cause
- rule
- guardrail test
