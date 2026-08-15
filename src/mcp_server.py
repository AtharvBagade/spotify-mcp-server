"""FastMCP Server initialization, tool registration, and ambient resources for Spotify MCP Server."""

from fastmcp import FastMCP
from src.config import load_settings
from src.client import get_spotify_client
from src.tools.users import (
    spotify_get_user_profile,
    spotify_get_top_tracks,
    spotify_get_top_artists,
    spotify_get_recently_played,
    spotify_get_saved_tracks,
)
from src.tools.catalog import (
    spotify_search_catalog,
    spotify_get_artist,
    spotify_get_artist_top_tracks,
    spotify_get_album,
)

settings = load_settings()

# Initialize FastMCP Server
mcp = FastMCP(name=settings.mcp_server_name)

# Register Modular Tools - Users & Library
mcp.add_tool(spotify_get_user_profile)
mcp.add_tool(spotify_get_top_tracks)
mcp.add_tool(spotify_get_top_artists)
mcp.add_tool(spotify_get_recently_played)
mcp.add_tool(spotify_get_saved_tracks)

# Register Modular Tools - Catalog Search & Metadata
mcp.add_tool(spotify_search_catalog)
mcp.add_tool(spotify_get_artist)
mcp.add_tool(spotify_get_artist_top_tracks)
mcp.add_tool(spotify_get_album)


# Ambient MCP Resources
@mcp.resource("spotify://user/profile")
async def get_user_profile_resource() -> str:
    """User profile metadata and product subscription context."""
    return await spotify_get_user_profile()


@mcp.resource("spotify://user/top-tracks")
async def get_user_top_tracks_resource() -> str:
    """Top listened tracks summary context for current user."""
    return await spotify_get_top_tracks(time_range="medium_term", limit=20)


@mcp.resource("spotify://user/top-artists")
async def get_user_top_artists_resource() -> str:
    """Top listened artists summary context for current user."""
    return await spotify_get_top_artists(time_range="medium_term", limit=20)


def run_server():
    """Run the FastMCP server via STDIO transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
