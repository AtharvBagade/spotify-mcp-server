#!/usr/bin/env python3
"""Spotify MCP Server - Model Context Protocol Server for Spotify API integration."""

import sys
from rich.console import Console
from rich.panel import Panel

from src.config import load_settings

console = Console()


def display_header():
    """Render Spotify MCP Server banner header."""
    header_text = (
        "[bold green]Spotify MCP Server[/bold green] - [bold cyan]Model Context Protocol Gateway[/bold cyan]\n"
        "[dim]Exposing Spotify playback, queue, playlists, recommendations, and search to AI agents[/dim]"
    )
    console.print(Panel(header_text, border_style="green", expand=False))


def main():
    """Main entrypoint for Spotify MCP Server."""
    display_header()
    settings = load_settings()
    console.print(f"[bold white]Server Name:[/bold white] {settings.mcp_server_name}")
    console.print(f"[bold white]Redirect URI:[/bold white] {settings.spotify_redirect_uri}")
    console.print("\n[bold yellow]Spotify MCP Server initialized. Ready for Milestone 1 setup.[/bold yellow]")


if __name__ == "__main__":
    main()
