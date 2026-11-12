from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ADA_",
        env_file=".env",
        extra="ignore",
    )

    # Environment
    environment: str = "development"
    debug: bool = False
    version: str = "0.1.0"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production-min-32-chars")
    device_token_ttl_hours: int = 24
    approval_ttl_minutes: int = 10

    # Supabase
    supabase_url: str = Field(default="")
    supabase_anon_key: str = Field(default="")
    supabase_service_role_key: str = Field(default="")  # Backend only. NEVER expose to clients.

    # Database (direct connection for LangGraph checkpointer)
    database_url: str = Field(default="")  # postgresql+asyncpg://...

    # Model Providers (all optional — only configure what you have)
    gemini_api_key: str = Field(default="")
    groq_api_key: str = Field(default="")
    openrouter_api_key: str = Field(default="")
    ollama_base_url: str = "http://127.0.0.1:11434"

    # Push Notifications
    fcm_server_key: str = Field(default="")

    # Logging
    log_level: str = "INFO"


def get_settings() -> Settings:
    return Settings()
