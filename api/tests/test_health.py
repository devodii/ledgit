import pytest
from fastapi.testclient import TestClient

from receipts.main import create_app
from receipts.settings import ConfigError, Settings, check_settings, get_settings


def test_health_returns_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://x:x@localhost/x")
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_missing_database_url_is_named() -> None:
    settings = Settings(_env_file=None, database_url="")
    with pytest.raises(ConfigError, match="DATABASE_URL"):
        check_settings(settings)


def test_real_llm_provider_requires_key_and_model() -> None:
    settings = Settings(_env_file=None, database_url="x", llm_provider="anthropic")
    assert settings.missing_required() == ["LLM_MODEL", "LLM_API_KEY"]
