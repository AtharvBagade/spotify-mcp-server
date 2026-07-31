"""Async Spotify API Client wrapper."""

from typing import Any, Dict, Optional
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
        headers = self.auth_manager.get_valid_access_token()
        req_headers = {
            "Authorization": f"Bearer {headers}",
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


# Global singleton instance
_spotify_client_instance: Optional[SpotifyClient] = None


def get_spotify_client() -> SpotifyClient:
    """Get or create singleton SpotifyClient instance."""
    global _spotify_client_instance
    if _spotify_client_instance is None:
        _spotify_client_instance = SpotifyClient()
    return _spotify_client_instance
