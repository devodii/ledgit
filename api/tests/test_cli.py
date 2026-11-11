import pytest

from receipts.cli import main
from receipts.settings import get_settings


def test_check_fails_naming_missing_variable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DATABASE_URL", "")
    get_settings.cache_clear()
    assert main(["check"]) == 1
    assert "DATABASE_URL" in capsys.readouterr().err


def test_check_passes_with_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://x:x@localhost/x")
    get_settings.cache_clear()
    assert main(["check"]) == 0
