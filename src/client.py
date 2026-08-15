"""Async Spotify API Client wrapper."""

from typing import Any, Dict, List, Optional
import httpx

from src.auth import SpotifyAuthManager
from src.config import load_settings

SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"


class SpotifyClient:
    """High-level async client for communicating with Spotify Web API."""

    def __init__(self, auth_manager: Optional[SpotifyAuthManager] = None):
        self.auth_manager = auth_manager or SpotifyAuthManager(load_settings())

    async def get_headers(self) -> Dict[str, str]:
        access_token = self.auth_manager.get_valid_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an authenticated async request to the Spotify Web API."""
        url = f"{SPOTIFY_API_BASE_URL}{endpoint}" if endpoint.startswith("/") else f"{SPOTIFY_API_BASE_URL}/{endpoint}"
        access_token = self.auth_manager.get_valid_access_token()
        req_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.request(
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
                    response = await client.request(
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

    async def get_user_profile(self) -> Dict[str, Any]:
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
        search_types: Optional[List[str]] = None,
        limit: int = 10,
        offset: int = 0,
        market: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search Spotify catalog across tracks, artists, albums, playlists, etc. (`GET /v1/search`)."""
        if search_types is None:
            search_types = ["track", "artist", "album"]
        type_str = ",".join(search_types)

        params: Dict[str, Any] = {
            "q": query,
            "type": type_str,
            "limit": limit,
            "offset": offset,
        }
        if market:
            params["market"] = market

        return await self.request("GET", "/search", params=params)

    async def get_artist(self, artist_id: str) -> Dict[str, Any]:
        """Fetch artist metadata (`GET /v1/artists/{id}`)."""
        return await self.request("GET", f"/artists/{artist_id}")

    async def get_artist_top_tracks(self, artist_id: str, market: str = "US") -> Dict[str, Any]:
        """Fetch top 10 tracks for an artist (`GET /v1/artists/{id}/top-tracks`)."""
        return await self.request("GET", f"/artists/{artist_id}/top-tracks", params={"market": market})

    async def get_album(self, album_id: str) -> Dict[str, Any]:
        """Fetch album details and tracklist (`GET /v1/albums/{id}`)."""
        return await self.request("GET", f"/albums/{album_id}")

    async def get_top_artists(
        self, time_range: str = "medium_term", limit: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        """Fetch user's top artists (`GET /v1/me/top/artists`)."""
        params = {"time_range": time_range, "limit": limit, "offset": offset}
        return await self.request("GET", "/me/top/artists", params=params)

    async def get_top_tracks(
        self, time_range: str = "medium_term", limit: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        """Fetch user's top tracks (`GET /v1/me/top/tracks`)."""
        params = {"time_range": time_range, "limit": limit, "offset": offset}
        return await self.request("GET", "/me/top/tracks", params=params)

    async def get_recently_played(self, limit: int = 20) -> Dict[str, Any]:
        """Fetch user's recently played tracks (`GET /v1/me/player/recently-played`)."""
        return await self.request("GET", "/me/player/recently-played", params={"limit": limit})

    async def get_saved_tracks(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Fetch user's saved ("Liked Songs") tracks (`GET /v1/me/tracks`)."""
        return await self.request("GET", "/me/tracks", params={"limit": limit, "offset": offset})


# Global singleton instance
_spotify_client_instance: Optional[SpotifyClient] = None


def get_spotify_client() -> SpotifyClient:
    """Get or create singleton SpotifyClient instance."""
    global _spotify_client_instance
    if _spotify_client_instance is None:
        _spotify_client_instance = SpotifyClient()
    return _spotify_client_instance
