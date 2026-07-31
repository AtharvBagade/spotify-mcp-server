"""Configuration settings for Spotify MCP Server."""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SpotifySettings(BaseSettings):
    """Configuration options loaded from environment variables or .env file."""

    spotify_client_id: str = Field(
        default="",
        description="Spotify App Client ID from developer dashboard",
    )
    spotify_client_secret: str = Field(
        default="",
        description="Spotify App Client Secret",
    )
    spotify_redirect_uri: str = Field(
        default="http://127.0.0.1:8888/callback",
        description="OAuth 2.0 Redirect URI",
    )
    spotify_token_cache_path: str = Field(
        default=".spotify_token.json",
        description="Path to store cached OAuth user access and refresh tokens",
    )
    mcp_server_name: str = Field(
        default="Spotify MCP Server",
        description="Display name for the MCP server",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def load_settings() -> SpotifySettings:
    """Load configuration settings."""
    return SpotifySettings()
