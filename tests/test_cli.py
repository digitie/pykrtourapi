from __future__ import annotations

from typing import Any

from visitkorea.cli import main
from visitkorea.models import Page


class DummyClient:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    def search_keyword(self, keyword: str, **kwargs: Any) -> Page[dict[str, str]]:
        return Page(
            items=({"keyword": keyword, "content_type_id": str(kwargs.get("content_type_id"))},),
            total_count=1,
            page_no=1,
            num_of_rows=10,
            raw={},
        )

    def location_based_list(self, **kwargs: Any) -> Page[dict[str, str]]:
        return Page(
            items=({"radius": str(kwargs["radius"])},),
            total_count=1,
            page_no=1,
            num_of_rows=10,
            raw={},
        )

    def detail_common(self, content_id: str) -> dict[str, str]:
        return {"content_id": content_id}

    def area_codes(self, **kwargs: Any) -> Page[dict[str, str]]:
        return Page(
            items=({"area_code": str(kwargs.get("area_code"))},),
            total_count=1,
            page_no=1,
            num_of_rows=10,
            raw={},
        )


def test_cli_keyword(monkeypatch, capsys):
    monkeypatch.setattr("visitkorea.cli.KrTourApiClient", DummyClient)

    assert main(["--service-key", "KEY", "keyword", "궁", "--content-type-id", "12"]) == 0

    out = capsys.readouterr().out
    assert '"keyword": "궁"' in out
    assert '"content_type_id": "12"' in out


def test_cli_other_commands(monkeypatch, capsys):
    monkeypatch.setattr("visitkorea.cli.KrTourApiClient", DummyClient)

    assert main(["--service-key", "KEY", "location", "--map-x", "1", "--map-y", "2"]) == 0
    assert '"radius": "1000"' in capsys.readouterr().out

    assert main(["--service-key", "KEY", "detail", "126508"]) == 0
    assert '"content_id": "126508"' in capsys.readouterr().out

    assert main(["--service-key", "KEY", "area-codes", "--area-code", "1"]) == 0
    assert '"area_code": "1"' in capsys.readouterr().out
