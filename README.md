# Spotify MCP Server

An open-source **Model Context Protocol (MCP) Server** exposing the Spotify Web API directly to AI assistants (Claude Desktop, Cursor, Antigravity, and autonomous LLM agents).

---

## 🎵 Capabilities & Features

The server bridges Spotify functionality natively to AI models across three core primitives:

1. **MCP Tools (30+ Actions)**:
   - **Playback Control**: Play, pause, skip, seek, volume, shuffle, repeat, device transfer.
   - **Queue Management**: Inspect active queue and append items.
   - **Playlist Curation**: Create/modify playlists, reorder tracks by BPM/energy, upload custom cover art.
   - **Catalog Search**: Unified search across tracks, artists, albums, playlists, shows, and audiobooks.
   - **Recommendations**: Audio-feature targeting (`valence`, `energy`, `danceability`, `tempo`) with genre/artist seeds.
   - **Library & Personalization**: Access top tracks/artists, liked songs, and listening history.

2. **MCP Resources (Real-time Context)**:
   - `spotify://player/current`: Live playback state, track metadata, progress.
   - `spotify://player/queue`: Live play queue list.
   - `spotify://user/top-tracks` & `spotify://user/top-artists`: Personal taste profiles.
   - `spotify://playlist/{playlist_id}`: Live playlist snapshots.

3. **MCP Prompts (AI Workflows)**:
   - `create_mood_playlist`: Mood-to-audio-target playlist generation.
   - `smart_queue_dj`: Vibe-matched queueing.
   - `listening_dna_report`: Audio taste profile breakdown.

---

## ⚙️ Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in your Spotify Developer credentials in `.env`:
   ```env
   SPOTIFY_CLIENT_ID="your_spotify_client_id_here"
   SPOTIFY_CLIENT_SECRET="your_spotify_client_secret_here"
   SPOTIFY_REDIRECT_URI="http://127.0.0.1:8888/callback"
   ```

---

## 🚀 Installation & Running

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run server entrypoint
python3 main.py
```

---

## 📖 Product Requirements & Roadmap

See [PRD.md](PRD.md) for full architectural specs and milestone details.
