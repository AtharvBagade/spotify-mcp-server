"""Unit tests for catalog search and metadata tools."""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.tools.catalog import (
    spotify_search_catalog,
    spotify_get_artist,
    spotify_get_artist_top_tracks,
    spotify_get_album,
)


@pytest.mark.asyncio
async def test_spotify_search_catalog():
    """Test spotify_search_catalog tool parsing."""
    mock_search_response = {
        "tracks": {
            "items": [
                {
                    "id": "t1",
                    "name": "Get Lucky",
                    "artists": [{"name": "Daft Punk"}],
                    "album": {"name": "Random Access Memories"},
                    "duration_ms": 240000,
                    "popularity": 85,
                    "uri": "spotify:track:t1",
                }
            ]
        },
        "artists": {
            "items": [
                {
                    "id": "a1",
                    "name": "Daft Punk",
                    "genres": ["synthpop", "electronic"],
                    "popularity": 90,
                    "followers": {"total": 5000000},
                    "uri": "spotify:artist:a1",
                }
            ]
        },
    }

    with patch("src.tools.catalog.get_spotify_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.search_catalog = AsyncMock(return_value=mock_search_response)
        mock_get_client.return_value = mock_client

        output = await spotify_search_catalog("Daft Punk")
        data = json.loads(output)

        assert "tracks" in data
        assert data["tracks"][0]["name"] == "Get Lucky"
        assert data["tracks"][0]["artists"] == ["Daft Punk"]
        assert "artists" in data
        assert data["artists"][0]["name"] == "Daft Punk"


@pytest.mark.asyncio
async def test_spotify_get_artist():
    """Test spotify_get_artist tool parsing."""
    mock_artist_response = {
        "id": "a1",
        "name": "Daft Punk",
        "genres": ["electronic"],
        "popularity": 92,
        "followers": {"total": 6000000},
        "uri": "spotify:artist:a1",
        "external_urls": {"spotify": "https://open.spotify.com/artist/a1"},
        "images": [{"url": "https://example.com/daftpunk.jpg"}],
    }

    with patch("src.tools.catalog.get_spotify_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_artist = AsyncMock(return_value=mock_artist_response)
        mock_get_client.return_value = mock_client

        output = await spotify_get_artist("a1")
        data = json.loads(output)

        assert data["id"] == "a1"
        assert data["name"] == "Daft Punk"
        assert data["popularity"] == 92
        assert data["image_url"] == "https://example.com/daftpunk.jpg"


@pytest.mark.asyncio
async def test_spotify_get_artist_top_tracks():
    """Test spotify_get_artist_top_tracks tool parsing."""
    mock_top_tracks_response = {
        "tracks": [
            {
                "id": "t1",
                "name": "One More Time",
                "artists": [{"name": "Daft Punk"}],
                "album": {"name": "Discovery"},
                "popularity": 88,
                "duration_ms": 320000,
                "uri": "spotify:track:t1",
            }
        ]
    }

    with patch("src.tools.catalog.get_spotify_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_artist_top_tracks = AsyncMock(return_value=mock_top_tracks_response)
        mock_get_client.return_value = mock_client

        output = await spotify_get_artist_top_tracks("a1", market="US")
        data = json.loads(output)

        assert len(data) == 1
        assert data[0]["name"] == "One More Time"
        assert data[0]["album"] == "Discovery"


@pytest.mark.asyncio
async def test_spotify_get_album():
    """Test spotify_get_album tool parsing."""
    mock_album_response = {
        "id": "alb1",
        "name": "Discovery",
        "album_type": "album",
        "artists": [{"name": "Daft Punk"}],
        "release_date": "2001-03-12",
        "total_tracks": 14,
        "label": "Virgin",
        "popularity": 90,
        "uri": "spotify:album:alb1",
        "tracks": {
            "items": [
                {
                    "id": "t1",
                    "track_number": 1,
                    "name": "One More Time",
                    "duration_ms": 320000,
                    "artists": [{"name": "Daft Punk"}],
                    "uri": "spotify:track:t1",
                }
            ]
        },
    }

    with patch("src.tools.catalog.get_spotify_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_album = AsyncMock(return_value=mock_album_response)
        mock_get_client.return_value = mock_client

        output = await spotify_get_album("alb1")
        data = json.loads(output)

        assert data["id"] == "alb1"
        assert data["name"] == "Discovery"
        assert data["total_tracks"] == 14
        assert len(data["tracks"]) == 1
        assert data["tracks"][0]["name"] == "One More Time"
