"""
Application configuration and environment management.

Loads configuration from environment variables. Ensure values are set in .env by the
orchestrator.
"""

import os
from functools import lru_cache

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Configuration model for application settings."""

    APP_NAME: str = Field(default="Event Management API", description="The application name.")
    APP_DESCRIPTION: str = Field(
        default="API system for managing events and attendees with authentication.",
        description="The application description used for API docs.",
    )
    APP_VERSION: str = Field(default="1.0.0", description="The application version.")
    API_PREFIX: str = Field(default="/api", description="The API prefix for all routes.")

    # Security
    SECRET_KEY: str = Field(
        default="CHANGE_ME",
        description="Secret key used for signing JWT tokens.",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        description="Access token expiration time in minutes.",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm.")

    # CORS
    CORS_ALLOW_ORIGINS: list[str] = Field(
        default_factory=lambda: ["*"],
        description="List of allowed CORS origins.",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow cookies/auth.")
    CORS_ALLOW_METHODS: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed HTTP methods.",
    )
    CORS_ALLOW_HEADERS: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed HTTP headers.",
    )

    # Database (using SQLite by default)
    DATABASE_URL: str = Field(
        default="sqlite:///./event_db.sqlite3",
        description="SQLAlchemy database URL (e.g., sqlite:///./db.sqlite3)",
    )

    # Optional site URL for auth flows
    SITE_URL: str | None = Field(
        default=None,
        description="Public site URL for email redirects if used by a frontend.",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Build Settings from environment variables overriding defaults when provided.
    """
    cors_origins = os.getenv("CORS_ALLOW_ORIGINS")
    cors_methods = os.getenv("CORS_ALLOW_METHODS")
    cors_headers = os.getenv("CORS_ALLOW_HEADERS")

    data = {
        "APP_NAME": os.getenv("APP_NAME"),
        "APP_DESCRIPTION": os.getenv("APP_DESCRIPTION"),
        "APP_VERSION": os.getenv("APP_VERSION"),
        "API_PREFIX": os.getenv("API_PREFIX"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
        "ALGORITHM": os.getenv("ALGORITHM"),
        "CORS_ALLOW_ORIGINS": cors_origins.split(",") if cors_origins else None,
        "CORS_ALLOW_CREDENTIALS": os.getenv("CORS_ALLOW_CREDENTIALS"),
        "CORS_ALLOW_METHODS": cors_methods.split(",") if cors_methods else None,
        "CORS_ALLOW_HEADERS": cors_headers.split(",") if cors_headers else None,
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "SITE_URL": os.getenv("SITE_URL"),
    }
    # Clean booleans and ints
    if isinstance(data["CORS_ALLOW_CREDENTIALS"], str):
        data["CORS_ALLOW_CREDENTIALS"] = data["CORS_ALLOW_CREDENTIALS"].lower() == "true"
    if (
        isinstance(data["ACCESS_TOKEN_EXPIRE_MINUTES"], str)
        and data["ACCESS_TOKEN_EXPIRE_MINUTES"].isdigit()
    ):
        data["ACCESS_TOKEN_EXPIRE_MINUTES"] = int(data["ACCESS_TOKEN_EXPIRE_MINUTES"])
    # Remove None entries to fallback on defaults
    data = {k: v for k, v in data.items() if v not in (None, "", [""])}
    return Settings(**data)
