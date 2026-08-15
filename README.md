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

## 🏗️ Architecture & Core Components

- **HTTP Library Layer (`src/lib/http.py`)**: Built on top of `httpx`. Exposes managed async (`HTTPClient`) and synchronous (`SyncHTTPClient`) clients with connection pooling, configurable timeouts, method shortcuts (`get`, `post`, `request_json`), and singleton instance management.
- **Auth Manager (`src/auth.py`)**: Handles Spotify OAuth 2.0 PKCE authentication, automatic local server callback listening (`http://127.0.0.1:8888/callback`), token caching, and background refresh.
- **Spotify Client (`src/client.py`)**: High-level async client wrapping the Spotify Web API, automatically attached to `HTTPClient` for connection pooling and token management.

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

## 🧪 Testing

Run the test suite using `pytest`:

```bash
pytest
```

The test suite covers:
- `tests/test_http_lib.py`: Unit tests for `HTTPClient`, `SyncHTTPClient`, context managers, singletons, and exception handling.
- `tests/test_auth.py`: OAuth PKCE flow and token cache management tests.
- `tests/test_client.py`: `SpotifyClient` request methods and token refresh retry tests.
- `tests/test_catalog.py`: Catalog search and metadata tool tests.
- `tests/test_users.py`: User profile, library, and personalization tool tests.
- `tests/test_player.py`: Playback controls, queue management, devices, and real-time MCP resource tests.
- `tests/test_playlists.py`: Playlist CRUD, track addition/removal, reordering/replacement, custom JPEG cover art upload, and `spotify://playlist/{playlist_id}` MCP resource tests.

---

## 📖 Product Requirements & Roadmap

See [PRD.md](PRD.md) for full architectural specs and milestone details.
