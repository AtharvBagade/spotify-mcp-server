"""User profile and personalization tools for Spotify MCP Server."""

import json
from typing import Any, Dict
from src.client import get_spotify_client


async def spotify_get_user_profile() -> str:
    """Fetch current authenticated user's Spotify profile details, country, and subscription status.

    Returns:
        JSON string containing user id, display_name, email, product (Premium/Free), country, followers, and spotify uri.
    """
    client = get_spotify_client()
    profile = await client.get_user_profile()
    return json.dumps(profile, indent=2)
