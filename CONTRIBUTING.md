# Contributing

## Development setup

```bash
pip install -e ".[dev]"
python -m pytest
```

## Pull request checklist

- Public behavior has tests.
- Default tests do not call the real API.
- New endpoints are documented in `krtourapi-api.md`.
- User-facing changes are documented in `README.md`.
- Repeated pitfalls are added to `docs/repeated-mistakes.md`.
- `CHANGELOG.md` is updated.

## Style

- Python 3.11+
- Typed public surfaces
- Frozen dataclasses for returned models
- Preserve provider-specific raw fields in `raw`
