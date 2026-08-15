"""Unit tests for Spotify OAuth PKCE Auth Manager."""

import time
from pathlib import Path

from src.auth import SpotifyAuthManager, generate_pkce_pair
from src.config import SpotifySettings


def test_generate_pkce_pair():
    """Test PKCE code_verifier and code_challenge generation."""
    verifier, challenge = generate_pkce_pair()
    assert len(verifier) >= 64
    assert len(challenge) > 0
    assert verifier != challenge


def test_token_cache_save_and_load(tmp_path: Path):
    """Test token caching to disk and loading."""
    token_file = tmp_path / "test_token.json"
    settings = SpotifySettings(spotify_token_cache_path=str(token_file))
    auth_manager = SpotifyAuthManager(settings)

    assert auth_manager.load_token_cache() is None

    test_data = {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "expires_in": 3600,
        "expires_at": int(time.time()) + 3600,
    }
    auth_manager.save_token_cache(test_data)
    loaded_data = auth_manager.load_token_cache()

    assert loaded_data is not None
    assert loaded_data["access_token"] == "mock_access_token"
    assert loaded_data["refresh_token"] == "mock_refresh_token"


def test_is_token_expired():
    """Test token expiration logic with buffer time."""
    settings = SpotifySettings()
    auth_manager = SpotifyAuthManager(settings)

    now = int(time.time())
    valid_token = {"expires_at": now + 600}
    expired_token = {"expires_at": now - 10}
    near_expired_token = {"expires_at": now + 30}  # Within default 60s buffer

    assert auth_manager.is_token_expired(valid_token) is False
    assert auth_manager.is_token_expired(expired_token) is True
    assert auth_manager.is_token_expired(near_expired_token) is True
