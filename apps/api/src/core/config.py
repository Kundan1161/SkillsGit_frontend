"""Runtime configuration.

Settings are loaded from environment variables (and an optional ``.env`` file
for local development). Values are read once at import time via the
``settings`` singleton — never reach for ``os.environ`` directly elsewhere.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["dev", "staging", "prod", "test"]


class Settings(BaseSettings):
    """Application settings.

    Variable names are prefix-free (e.g. ``DATABASE_URL``, not
    ``SKILLSGIT_DATABASE_URL``) per the spec in ``01-tech-stack-and-repo.md``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Environment ────────────────────────────────────────────────────
    ENV: Environment = "dev"
    GIT_COMMIT: str = "dev"

    # ── Database ───────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://skillsgit:skillsgit@localhost:5432/skillsgit"
    )

    # ── Redis ──────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Object storage ────────────────────────────────────────────────
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "skillsgit"
    S3_SECRET_KEY: SecretStr = SecretStr("skillsgit")
    S3_BUCKET: str = "skillsgit-skills"
    SKG_STORAGE_MOCK: bool = False

    # ── Stripe ─────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: SecretStr = SecretStr("sk_test_placeholder")
    STRIPE_WEBHOOK_SECRET: SecretStr = SecretStr("whsec_placeholder")

    # ── Secrets ────────────────────────────────────────────────────────
    JWT_SECRET: SecretStr = SecretStr(
        "dev-jwt-secret-change-me-please-32+chars"
    )
    PLATFORM_HMAC_KEY: SecretStr = SecretStr(
        "dev-hmac-key-change-me-please-32+chars"
    )

    # ── Platform economics ─────────────────────────────────────────────
    PLATFORM_FEE_PERCENT: float = 20.0

    # ── Email ─────────────────────────────────────────────────────────
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_FROM: str = "noreply@skillsgit.local"

    # ── CORS ──────────────────────────────────────────────────────────
    # NoDecode keeps pydantic-settings from trying JSON-parse the env value;
    # the field_validator below handles the comma-separated form.
    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:3001"],
    )

    # ── OAuth (optional) ──────────────────────────────────────────────
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: SecretStr = SecretStr("")
    GITHUB_OAUTH_CLIENT_ID: str = ""
    GITHUB_OAUTH_CLIENT_SECRET: SecretStr = SecretStr("")

    # ── AI providers (optional; Phase 3+) ─────────────────────────────
    OPENAI_API_KEY: SecretStr = SecretStr("")
    ANTHROPIC_API_KEY: SecretStr = SecretStr("")

    # ── Capture LLM (ADR-008) ─────────────────────────────────────────
    # The capture flow's neuron-draft extraction uses a platform-managed
    # Claude key (ADR-008). The model defaults to claude-sonnet-4-6 (in
    # the validator's allowlist). The stub flag swaps in
    # ``tests/stubs/llm.py`` for deterministic CI runs; ``SKG_LLM_STUB``
    # is a legacy alias accepted for backward compat with the test-plan.
    SKG_CAPTURE_LLM_MODEL: str = "claude-sonnet-4-6"
    SKG_CAPTURE_LLM_STUB: bool = False
    SKG_CAPTURE_QUOTA_PER_MONTH: int = 10

    # ── Derived helpers ───────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.ENV == "prod"

    @property
    def is_test(self) -> bool:
        return self.ENV == "test"

    @property
    def session_cookie_secure(self) -> bool:
        # In dev we use http://localhost, so Secure cookies would not be sent.
        return self.ENV in ("staging", "prod")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    @field_validator("PLATFORM_FEE_PERCENT")
    @classmethod
    def _validate_fee(cls, value: float) -> float:
        if not 0 <= value <= 100:
            raise ValueError("PLATFORM_FEE_PERCENT must be in [0, 100]")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached settings instance.

    Used as a FastAPI dependency. Tests can clear the cache and override env
    vars to reload.
    """
    return Settings()


settings: Settings = get_settings()
