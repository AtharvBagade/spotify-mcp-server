"""FastMCP Server initialization and tool registration for Spotify MCP Server."""

from fastmcp import FastMCP
from src.config import load_settings
from src.tools.users import spotify_get_user_profile

settings = load_settings()

# Initialize FastMCP Server
mcp = FastMCP(name=settings.mcp_server_name)

# Register modular tools
mcp.add_tool(spotify_get_user_profile)


def run_server():
    """Run the FastMCP server via STDIO transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
