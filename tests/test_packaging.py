from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_distribution_uses_visitkorea_import_name() -> None:
    package = importlib.import_module("visitkorea")
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert package.KrTourApiClient.__name__ == "KrTourApiClient"
    assert pyproject["project"]["name"] == "python-visitkorea-api"
    assert pyproject["project"]["scripts"]["visitkorea"] == "visitkorea.cli:main"


def test_source_layout_is_configured_for_visitkorea_package() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package_find = pyproject["tool"]["setuptools"]["packages"]["find"]

    assert package_find["where"] == ["src"]
    assert package_find["include"] == ["visitkorea*"]
    assert (ROOT / "src" / "visitkorea" / "py.typed").exists()
