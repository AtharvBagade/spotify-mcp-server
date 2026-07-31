"""Unit tests for SpotifyClient and user tools."""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.client import SpotifyClient
from src.tools.users import spotify_get_user_profile


@pytest.mark.asyncio
async def test_get_user_profile_parsing():
    """Test SpotifyClient.get_user_profile metadata formatting."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.get_valid_access_token.return_value = "mock_token"

    client = SpotifyClient(auth_manager=mock_auth_manager)

    mock_api_response = {
        "id": "test_user_id",
        "display_name": "Test User",
        "email": "test@example.com",
        "product": "premium",
        "country": "US",
        "followers": {"total": 42},
        "uri": "spotify:user:test_user_id",
        "external_urls": {"spotify": "https://open.spotify.com/user/test_user_id"},
        "images": [{"url": "https://example.com/avatar.jpg"}],
    }

    with patch.object(client, "request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_api_response
        profile = await client.get_user_profile()

        assert profile["id"] == "test_user_id"
        assert profile["display_name"] == "Test User"
        assert profile["email"] == "test@example.com"
        assert profile["product"] == "premium"
        assert profile["followers"] == 42
        assert profile["image_url"] == "https://example.com/avatar.jpg"
        mock_request.assert_called_once_with("GET", "/me")


@pytest.mark.asyncio
async def test_spotify_get_user_profile_tool():
    """Test spotify_get_user_profile MCP tool function output."""
    mock_profile = {
        "id": "mcp_user",
        "display_name": "MCP User",
        "product": "premium",
    }
    with patch("src.tools.users.get_spotify_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_user_profile = AsyncMock(return_value=mock_profile)
        mock_get_client.return_value = mock_client

        tool_output = await spotify_get_user_profile()
        parsed_output = json.loads(tool_output)

        assert parsed_output["id"] == "mcp_user"
        assert parsed_output["display_name"] == "MCP User"
        assert parsed_output["product"] == "premium"
