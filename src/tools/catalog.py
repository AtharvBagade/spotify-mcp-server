"""Catalog search and metadata retrieval tools for Spotify MCP Server."""

import json
from typing import Any, Dict, List, Optional
from src.client import get_spotify_client


async def spotify_search_catalog(
    query: str,
    search_types: Optional[List[str]] = None,
    limit: int = 10,
    offset: int = 0,
    market: Optional[str] = None,
) -> str:
    """Search the Spotify catalog across tracks, artists, albums, playlists, etc.

    Args:
        query: Search query string (e.g. "Daft Punk", "Bohemian Rhapsody").
        search_types: Optional list of item types to search ("track", "artist", "album", "playlist", "show", "episode", "audiobook"). Defaults to ["track", "artist", "album"].
        limit: Number of items per type to return (1-50, default 10).
        offset: Result offset index (default 0).
        market: Optional ISO 3166-1 alpha-2 country code (e.g. "US").

    Returns:
        JSON string of matching search items grouped by category.
    """
    client = get_spotify_client()
    raw_results = await client.search_catalog(
        query=query,
        search_types=search_types,
        limit=limit,
        offset=offset,
        market=market,
    )

    formatted_results: Dict[str, Any] = {}

    if "tracks" in raw_results:
        formatted_results["tracks"] = [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "artists": [a.get("name") for a in item.get("artists", [])],
                "album": item.get("album", {}).get("name"),
                "duration_ms": item.get("duration_ms"),
                "popularity": item.get("popularity"),
                "uri": item.get("uri"),
            }
            for item in raw_results["tracks"].get("items", [])
        ]

    if "artists" in raw_results:
        formatted_results["artists"] = [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "genres": item.get("genres", []),
                "popularity": item.get("popularity"),
                "followers": item.get("followers", {}).get("total", 0),
                "uri": item.get("uri"),
            }
            for item in raw_results["artists"].get("items", [])
        ]

    if "albums" in raw_results:
        formatted_results["albums"] = [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "artists": [a.get("name") for a in item.get("artists", [])],
                "release_date": item.get("release_date"),
                "total_tracks": item.get("total_tracks"),
                "uri": item.get("uri"),
            }
            for item in raw_results["albums"].get("items", [])
        ]

    if "playlists" in raw_results:
        formatted_results["playlists"] = [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "owner": item.get("owner", {}).get("display_name"),
                "tracks_total": item.get("tracks", {}).get("total", 0),
                "uri": item.get("uri"),
            }
            for item in raw_results["playlists"].get("items", [])
        ]

    return json.dumps(formatted_results, indent=2)


async def spotify_get_artist(artist_id: str) -> str:
    """Fetch metadata for a specific Spotify artist.

    Args:
        artist_id: The Spotify ID or URI for the artist.

    Returns:
        JSON string containing artist bio, genres, popularity score, follower count, and external URLs.
    """
    clean_id = artist_id.replace("spotify:artist:", "")
    client = get_spotify_client()
    raw = await client.get_artist(clean_id)

    images = raw.get("images", [])
    image_url = images[0]["url"] if images else None

    formatted = {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "genres": raw.get("genres", []),
        "popularity": raw.get("popularity"),
        "followers": raw.get("followers", {}).get("total", 0),
        "uri": raw.get("uri"),
        "spotify_url": raw.get("external_urls", {}).get("spotify"),
        "image_url": image_url,
    }
    return json.dumps(formatted, indent=2)


async def spotify_get_artist_top_tracks(artist_id: str, market: str = "US") -> str:
    """Fetch top 10 tracks for a specific artist by country market.

    Args:
        artist_id: The Spotify ID or URI for the artist.
        market: ISO 3166-1 alpha-2 country code (default "US").

    Returns:
        JSON list of artist's top tracks with track name, album, popularity, duration, and URI.
    """
    clean_id = artist_id.replace("spotify:artist:", "")
    client = get_spotify_client()
    raw = await client.get_artist_top_tracks(clean_id, market=market)

    top_tracks = [
        {
            "id": t.get("id"),
            "name": t.get("name"),
            "artists": [a.get("name") for a in t.get("artists", [])],
            "album": t.get("album", {}).get("name"),
            "popularity": t.get("popularity"),
            "duration_ms": t.get("duration_ms"),
            "uri": t.get("uri"),
        }
        for t in raw.get("tracks", [])
    ]
    return json.dumps(top_tracks, indent=2)


async def spotify_get_album(album_id: str) -> str:
    """Fetch metadata and complete tracklist for a Spotify album.

    Args:
        album_id: The Spotify ID or URI for the album.

    Returns:
        JSON string containing album name, artists, release date, label, popularity, and tracks list.
    """
    clean_id = album_id.replace("spotify:album:", "")
    client = get_spotify_client()
    raw = await client.get_album(clean_id)

    tracks = [
        {
            "id": t.get("id"),
            "track_number": t.get("track_number"),
            "name": t.get("name"),
            "duration_ms": t.get("duration_ms"),
            "artists": [a.get("name") for a in t.get("artists", [])],
            "uri": t.get("uri"),
        }
        for t in raw.get("tracks", {}).get("items", [])
    ]

    formatted = {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "album_type": raw.get("album_type"),
        "artists": [a.get("name") for a in raw.get("artists", [])],
        "release_date": raw.get("release_date"),
        "total_tracks": raw.get("total_tracks"),
        "label": raw.get("label"),
        "popularity": raw.get("popularity"),
        "uri": raw.get("uri"),
        "tracks": tracks,
    }
    return json.dumps(formatted, indent=2)
