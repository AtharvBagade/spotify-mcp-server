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


@pytest.mark.asyncio
async def test_client_player_methods():
    """Test client-level player, devices, and queue request construction."""
    client = SpotifyClient(auth_manager=MagicMock())

    with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {}

        # get_playback_state
        await client.get_playback_state(market="US")
        mock_req.assert_awaited_with("GET", "/me/player", params={"market": "US"})

        # get_currently_playing
        await client.get_currently_playing(market="GB")
        mock_req.assert_awaited_with("GET", "/me/player/currently-playing", params={"market": "GB"})

        # get_available_devices
        await client.get_available_devices()
        mock_req.assert_awaited_with("GET", "/me/player/devices")

        # transfer_playback
        await client.transfer_playback(device_id="dev1", play=True)
        mock_req.assert_awaited_with("PUT", "/me/player", json_data={"device_ids": ["dev1"], "play": True})

        # play with context
        await client.play(device_id="dev1", context_uri="spotify:album:1", position_ms=5000)
        mock_req.assert_awaited_with(
            "PUT",
            "/me/player/play",
            params={"device_id": "dev1"},
            json_data={"context_uri": "spotify:album:1", "position_ms": 5000},
        )

        # pause
        await client.pause(device_id="dev1")
        mock_req.assert_awaited_with("PUT", "/me/player/pause", params={"device_id": "dev1"})

        # next & prev
        await client.skip_to_next(device_id="dev1")
        mock_req.assert_awaited_with("POST", "/me/player/next", params={"device_id": "dev1"})

        await client.skip_to_previous()
        mock_req.assert_awaited_with("POST", "/me/player/previous", params=None)

        # seek & volume
        await client.seek_to_position(position_ms=10000, device_id="dev1")
        mock_req.assert_awaited_with("PUT", "/me/player/seek", params={"position_ms": 10000, "device_id": "dev1"})

        await client.set_volume(volume_percent=70, device_id="dev1")
        mock_req.assert_awaited_with("PUT", "/me/player/volume", params={"volume_percent": 70, "device_id": "dev1"})

        # shuffle & repeat
        await client.toggle_shuffle(state=True, device_id="dev1")
        mock_req.assert_awaited_with("PUT", "/me/player/shuffle", params={"state": "true", "device_id": "dev1"})

        await client.set_repeat_mode(state="track", device_id="dev1")
        mock_req.assert_awaited_with("PUT", "/me/player/repeat", params={"state": "track", "device_id": "dev1"})

        # queue
        await client.get_queue()
        mock_req.assert_awaited_with("GET", "/me/player/queue")

        await client.add_to_queue(uri="spotify:track:123", device_id="dev1")
        mock_req.assert_awaited_with("POST", "/me/player/queue", params={"uri": "spotify:track:123", "device_id": "dev1"})
