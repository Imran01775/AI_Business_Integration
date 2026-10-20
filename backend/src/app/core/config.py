"""Infrastructure configuration (R-CFG-08)."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class AppConfig(BaseSettings):
    """Validated environment configuration; invalid values fail at startup."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: AppEnv = Field(alias="APP_ENV", default=AppEnv.DEVELOPMENT)
    app_debug: bool = Field(alias="APP_DEBUG", default=False)
    app_public_url: str = Field(alias="APP_PUBLIC_URL", default="http://localhost:8000")

    database_url: str = Field(
        alias="DATABASE_URL",
        default="postgresql+asyncpg://sales_agent:sales_agent@localhost:5432/sales_agent",
    )
    database_owner_url: str | None = Field(alias="DATABASE_OWNER_URL", default=None)
    database_rw_url: str | None = Field(alias="DATABASE_RW_URL", default=None)
    redis_url: str = Field(alias="REDIS_URL", default="redis://localhost:6379/0")

    s3_endpoint_url: str = Field(alias="S3_ENDPOINT_URL", default="http://localhost:9000")
    s3_access_key_id: str = Field(alias="S3_ACCESS_KEY_ID", default="minioadmin")
    s3_secret_access_key: str = Field(alias="S3_SECRET_ACCESS_KEY", default="minioadmin")
    s3_bucket: str = Field(alias="S3_BUCKET", default="sales-agent")
    s3_region: str = Field(alias="S3_REGION", default="us-east-1")
    s3_use_ssl: bool = Field(alias="S3_USE_SSL", default=False)

    smtp_host: str = Field(alias="SMTP_HOST", default="localhost")
    smtp_port: int = Field(alias="SMTP_PORT", default=1025)
    smtp_from: str = Field(alias="SMTP_FROM", default="noreply@localhost")
    smtp_use_tls: bool = Field(alias="SMTP_USE_TLS", default=False)

    jwt_secret: str = Field(
        alias="JWT_SECRET",
        min_length=16,
        default="dev-only-change-in-production-32",
    )
    jwt_access_token_ttl_seconds: int = Field(alias="JWT_ACCESS_TOKEN_TTL_SECONDS", default=900)
    jwt_algorithm: str = Field(alias="JWT_ALGORITHM", default="HS256")
    jwt_refresh_token_ttl_days: int = Field(alias="JWT_REFRESH_TOKEN_TTL_DAYS", default=30)
    auth_max_sessions: int = Field(alias="AUTH_MAX_SESSIONS", default=10)
    auth_cookie_secure: bool = Field(alias="AUTH_COOKIE_SECURE", default=False)
    auth_cookie_domain: str | None = Field(alias="AUTH_COOKIE_DOMAIN", default=None)
    secrets_encryption_key: str = Field(
        alias="SECRETS_ENCRYPTION_KEY",
        min_length=16,
        default="dev-only-secrets-key-32bytes!!",
    )
    secrets_key_version: int = Field(alias="SECRETS_KEY_VERSION", default=1)

    otel_exporter_otlp_endpoint: str | None = Field(
        alias="OTEL_EXPORTER_OTLP_ENDPOINT", default=None
    )
    otel_service_name: str = Field(alias="OTEL_SERVICE_NAME", default="sales-agent-api")
    glitchtip_dsn: str | None = Field(alias="GLITCHTIP_DSN", default=None)

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
    )
    max_request_body_bytes: int = Field(default=2 * 1024 * 1024)
    use_in_memory_adapters: bool = Field(alias="USE_IN_MEMORY_ADAPTERS", default=False)

    ai_platform_mode: Literal["in_process", "http"] = Field(
        alias="AI_PLATFORM_MODE",
        default="in_process",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def _ensure_asyncpg_driver(cls, value: object) -> object:
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @property
    def is_test(self) -> bool:
        return self.app_env == AppEnv.TEST
