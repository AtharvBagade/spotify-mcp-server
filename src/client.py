"""Async Spotify API Client wrapper."""

from typing import Any

from src.auth import SpotifyAuthManager
from src.config import load_settings
from src.lib.http import HTTPClient, get_http_client

SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"


class SpotifyClient:
    """High-level async client for communicating with Spotify Web API."""

    def __init__(
        self,
        auth_manager: SpotifyAuthManager | None = None,
        http_client: HTTPClient | None = None,
    ):
        self.auth_manager = auth_manager or SpotifyAuthManager(load_settings())
        self._http_client = http_client

    @property
    def http_client(self) -> HTTPClient:
        if self._http_client is None:
            self._http_client = get_http_client()
        return self._http_client

    async def get_headers(self) -> dict[str, str]:
        access_token = self.auth_manager.get_valid_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated async request to the Spotify Web API."""
        url = f"{SPOTIFY_API_BASE_URL}{endpoint}" if endpoint.startswith("/") else f"{SPOTIFY_API_BASE_URL}/{endpoint}"
        access_token = self.auth_manager.get_valid_access_token()
        req_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = await self.http_client.request(
            method=method.upper(),
            url=url,
            headers=req_headers,
            params=params,
            json=json_data,
        )

        # Retry once on 401 Unauthorized by forcing a token refresh
        if response.status_code == 401:
            token_data = self.auth_manager.load_token_cache()
            if token_data and "refresh_token" in token_data:
                self.auth_manager.refresh_access_token(token_data["refresh_token"])
                new_token = self.auth_manager.get_valid_access_token()
                req_headers["Authorization"] = f"Bearer {new_token}"
                response = await self.http_client.request(
                    method=method.upper(),
                    url=url,
                    headers=req_headers,
                    params=params,
                    json=json_data,
                )

        response.raise_for_status()
        if response.status_code == 204:
            return {}
        return response.json()

    async def get_user_profile(self) -> dict[str, Any]:
        """Fetch current authenticated user's profile details (`GET /v1/me`)."""
        raw_data = await self.request("GET", "/me")
        images = raw_data.get("images", [])
        image_url = images[0]["url"] if images else None

        return {
            "id": raw_data.get("id"),
            "display_name": raw_data.get("display_name"),
            "email": raw_data.get("email"),
            "product": raw_data.get("product"),
            "country": raw_data.get("country"),
            "followers": raw_data.get("followers", {}).get("total", 0),
            "uri": raw_data.get("uri"),
            "profile_url": raw_data.get("external_urls", {}).get("spotify"),
            "image_url": image_url,
        }

    async def search_catalog(
        self,
        query: str,
        search_types: list[str] | None = None,
        limit: int = 10,
        offset: int = 0,
        market: str | None = None,
    ) -> dict[str, Any]:
        """Search Spotify catalog across tracks, artists, albums, playlists, etc. (`GET /v1/search`)."""
        if search_types is None:
            search_types = ["track", "artist", "album"]
        type_str = ",".join(search_types)

        params: dict[str, Any] = {
            "q": query,
            "type": type_str,
            "limit": limit,
            "offset": offset,
        }
        if market:
            params["market"] = market

        return await self.request("GET", "/search", params=params)

    async def get_artist(self, artist_id: str) -> dict[str, Any]:
        """Fetch artist metadata (`GET /v1/artists/{id}`)."""
        return await self.request("GET", f"/artists/{artist_id}")

    async def get_artist_top_tracks(self, artist_id: str, market: str = "US") -> dict[str, Any]:
        """Fetch top 10 tracks for an artist (`GET /v1/artists/{id}/top-tracks`)."""
        return await self.request("GET", f"/artists/{artist_id}/top-tracks", params={"market": market})

    async def get_album(self, album_id: str) -> dict[str, Any]:
        """Fetch album details and tracklist (`GET /v1/albums/{id}`)."""
        return await self.request("GET", f"/albums/{album_id}")

    async def get_top_artists(
        self, time_range: str = "medium_term", limit: int = 20, offset: int = 0
    ) -> dict[str, Any]:
        """Fetch user's top artists (`GET /v1/me/top/artists`)."""
        params = {"time_range": time_range, "limit": limit, "offset": offset}
        return await self.request("GET", "/me/top/artists", params=params)

    async def get_top_tracks(
        self, time_range: str = "medium_term", limit: int = 20, offset: int = 0
    ) -> dict[str, Any]:
        """Fetch user's top tracks (`GET /v1/me/top/tracks`)."""
        params = {"time_range": time_range, "limit": limit, "offset": offset}
        return await self.request("GET", "/me/top/tracks", params=params)

    async def get_recently_played(self, limit: int = 20) -> dict[str, Any]:
        """Fetch user's recently played tracks (`GET /v1/me/player/recently-played`)."""
        return await self.request("GET", "/me/player/recently-played", params={"limit": limit})

    async def get_saved_tracks(self, limit: int = 20, offset: int = 0) -> dict[str, Any]:
        """Fetch user's saved ("Liked Songs") tracks (`GET /v1/me/tracks`)."""
        return await self.request("GET", "/me/tracks", params={"limit": limit, "offset": offset})


# Global singleton instance
_spotify_client_instance: SpotifyClient | None = None


def get_spotify_client() -> SpotifyClient:
    """Get or create singleton SpotifyClient instance."""
    global _spotify_client_instance
    if _spotify_client_instance is None:
        _spotify_client_instance = SpotifyClient()
    return _spotify_client_instance
