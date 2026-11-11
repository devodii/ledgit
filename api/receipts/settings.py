from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class ConfigError(Exception):
    pass


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: Literal["local", "production"] = "local"
    database_url: str = ""
    api_cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    http_contact_url: str = "https://github.com/devodii/ledgit"
    http_rate_limit_rps: float = 1.0
    http_timeout_seconds: float = 20.0
    dns_fallback: bool = True
    cache_dir: Path = REPO_ROOT / "data" / "cache"
    tasks_dir: Path = REPO_ROOT / "data" / "tasks"
    data_dir: Path = REPO_ROOT / "data"
    fixtures_dir: Path = REPO_ROOT / "fixtures"
    evals_dir: Path = REPO_ROOT / "evals"

    horizon_url: str = "https://horizon.stellar.lobstr.co"
    horizon_testnet_url: str = "https://horizon-testnet.stellar.org"
    soroban_rpc_url: str = "https://mainnet.sorobanrpc.com"
    soroban_rpc_testnet_url: str = "https://soroban-testnet.stellar.org"
    stellar_expert_url: str = "https://api.stellar.expert"

    verify_min_asset_holders: int = 10
    verify_contract_activity_days: int = 30
    verify_pending_days: int = 14
    pipeline_min_confidence: float = Field(default=0.7, ge=0, le=1)

    llm_provider: Literal["claude_code", "anthropic", "openai", "fake"] = "fake"
    llm_model: str = ""
    llm_api_key: str = ""
    llm_max_tokens: int = 4096

    youtube_api_key: str = ""

    browser_headful: bool = False
    browser_profile_dir: Path = REPO_ROOT / "data" / "cache" / "browser"
    browser_timeout_ms: int = 30000

    scheduler_enabled: bool = True
    verify_cron: str = "0 6 * * *"

    def missing_required(self) -> list[str]:
        missing: list[str] = []
        if not self.database_url:
            missing.append("DATABASE_URL")
        if self.llm_provider in ("anthropic", "openai"):
            if not self.llm_model:
                missing.append("LLM_MODEL")
            if not self.llm_api_key:
                missing.append("LLM_API_KEY")
        return missing


@lru_cache
def get_settings() -> Settings:
    return Settings()


def check_settings(settings: Settings) -> None:
    missing = settings.missing_required()
    if missing:
        names = ", ".join(missing)
        raise ConfigError(
            f"Missing required environment variables: {names}. "
            "Copy .env.example to .env and fill them in."
        )
