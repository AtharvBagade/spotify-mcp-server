# Product Requirements Document (PRD): Spotify MCP Server

## 1. Executive Summary & Core Objective
The **Spotify MCP Server** is an open-source, full-featured Model Context Protocol (MCP) server that exposes the Spotify Web API directly to AI clients (Claude Desktop, Cursor, Antigravity, and autonomous LLM agents).

By pivoting from a standalone app to a native MCP Server, any compliant LLM can seamlessly control Spotify playback, manage and curate playlists, inspect user listening history, search the Spotify catalog, perform audio-feature music analysis, and generate AI-driven recommendation queues via standard MCP **Tools**, **Resources**, and **Prompts**.

---

## 2. Architecture & MCP Primitive Mapping

The Spotify MCP Server exposes three core MCP primitives:
- **MCP Tools**: Executable actions (playback control, playlist CRUD, queueing, search, recommendation generation).
- **MCP Resources**: Passive, read-only URIs (`spotify://player/current`, `spotify://user/top-tracks`, `spotify://playlist/{id}`) that provide real-time ambient context to the LLM.
- **MCP Prompts**: Pre-packaged, multi-step LLM workflows (e.g. `create_mood_playlist`, `smart_queue_dj`, `listening_dna_report`).

---

## 3. Core Functional Feature Scopes (MCP Tools)

### 3.1 Playback Control & Player Management
- `spotify_play`: Resume or start playback (supports `context_uri`, `uris`, `offset`, `position_ms`).
- `spotify_pause`: Pause playback on active device.
- `spotify_skip_to_next`: Skip to next track in queue/context.
- `spotify_skip_to_previous`: Skip to previous track.
- `spotify_seek_to_position`: Seek to timestamp in milliseconds (`position_ms`).
- `spotify_set_volume`: Set volume percentage (0–100%).
- `spotify_set_repeat_mode`: Set repeat mode (`off`, `track`, `context`).
- `spotify_toggle_shuffle`: Toggle shuffle on/off (`state: boolean`).
- `spotify_get_playback_state`: Retrieve active device, progress, repeat/shuffle state.
- `spotify_get_currently_playing`: Get metadata for currently playing track/episode.
- `spotify_get_available_devices`: List connected devices (desktop, mobile, smart speakers).
- `spotify_transfer_playback`: Switch active playback to a specified `device_id`.

### 3.2 Queue Management
- `spotify_get_queue`: Fetch current playback queue listing.
- `spotify_add_to_queue`: Append track or episode URI to queue.

### 3.3 Playlist Management & Curation
- `spotify_get_user_playlists`: List user's created and followed playlists.
- `spotify_get_playlist`: Get metadata, follower count, and owner info for a playlist.
- `spotify_get_playlist_items`: Retrieve tracks/episodes inside a playlist.
- `spotify_create_playlist`: Create public/private playlists with title and description.
- `spotify_add_tracks_to_playlist`: Add tracks to a playlist.
- `spotify_remove_tracks_from_playlist`: Remove tracks by URI/position.
- `spotify_reorder_playlist_tracks`: Reorder tracks (for energy/BPM curves).
- `spotify_update_playlist_details`: Update playlist title, description, or privacy settings.
- `spotify_upload_playlist_cover`: Set custom JPEG cover image (base64).

### 3.4 Catalog Search & Metadata Retrieval
- `spotify_search_catalog`: Search tracks, artists, albums, playlists, shows, episodes, audiobooks.
- `spotify_get_artist`: Fetch artist bio, popularity, genres, followers.
- `spotify_get_artist_top_tracks`: Get top 10 tracks for an artist by country code.
- `spotify_get_artist_related_artists`: Discover related artists.
- `spotify_get_album`: Fetch album details and track listings.

### 3.5 Recommendations & Audio Feature Curation
- `spotify_get_recommendations`: Seeded discovery engine supporting:
  - Seeds: `seed_artists`, `seed_genres`, `seed_tracks` (up to 5 combined).
  - Target / Min / Max audio parameters: `target_danceability`, `target_energy`, `target_valence` (mood), `target_tempo` (BPM), `target_acousticness`, `target_instrumentalness`, `target_speechiness`, `target_popularity`.
- `spotify_get_audio_features`: Retrieve acoustic features (BPM, Key, Valence, Energy) for track IDs.
- `spotify_get_audio_analysis`: Get structural low-level acoustic breakdown (beats, bars, sections).
- `spotify_get_available_genre_seeds`: List available genre seeds for recommendations.

### 3.6 Personalization & Library Management
- `spotify_get_user_profile`: Fetch user profile details and subscription level (Premium/Free).
- `spotify_get_top_artists` / `spotify_get_top_tracks`: Get top user items across time ranges (`short_term`, `medium_term`, `long_term`).
- `spotify_get_recently_played`: Get recent listening history with timestamps.
- `spotify_get_saved_tracks` / `spotify_save_tracks` / `spotify_remove_saved_tracks`: Manage "Liked Songs" library.

---

## 4. MCP Resources Specification

| Resource URI Scheme | Description |
| :--- | :--- |
| `spotify://user/profile` | User profile metadata & product subscription type. |
| `spotify://player/current` | Active player state, playing track info, progress, and device. |
| `spotify://player/queue` | Live snapshot of user's playback queue. |
| `spotify://user/top-artists` | Top artists list over configurable time ranges. |
| `spotify://user/top-tracks` | Top tracks list over configurable time ranges. |
| `spotify://playlist/{playlist_id}` | Full tracklist and metadata snapshot for a specific playlist. |

---

## 5. MCP Prompts Specification

1. **`create_mood_playlist`**
   - *Description*: Prompts the LLM to convert human mood descriptions into target audio parameters, query recommendations, and create a custom playlist.
2. **`smart_queue_dj`**
   - *Description*: Inspects `spotify://player/current` and queues songs matching the ongoing vibe.
3. **`listening_dna_report`**
   - *Description*: Generates a detailed musical taste profile based on `spotify://user/top-tracks` and audio features.
4. **`playlist_cleaner_and_organizer`**
   - *Description*: Reorders tracks in an existing playlist into a smooth harmonic or energy progression.

---

## 6. Authentication & Security Setup

The server uses **OAuth 2.0 PKCE Flow** for local token authorization with automatic token refresh.

```env
# Spotify OAuth Credentials
SPOTIFY_CLIENT_ID="your_spotify_client_id_here"
SPOTIFY_REDIRECT_URI="http://127.0.0.1:8888/callback"
```

### Required Scopes:
- `user-read-playback-state`
- `user-modify-playback-state`
- `user-read-currently-playing`
- `playlist-read-private`
- `playlist-read-collaborative`
- `playlist-modify-public`
- `playlist-modify-private`
- `user-library-read`
- `user-library-modify`
- `user-top-read`
- `user-read-recently-played`
- `user-follow-read`

---

## 7. Implementation Roadmap & Milestones

### 🚩 Milestone 1: Project Foundation & Spotify OAuth Architecture
- Integrate `fastmcp` or `mcp` SDK and `httpx` in `pyproject.toml`.
- Implement `SpotifyAuthManager` for OAuth 2.0 PKCE flow (`http://127.0.0.1:8888/callback`).
- Secure token storage & auto-refresh mechanism (`.spotify_token.json`).
- Implement async `SpotifyClient` wrapper and first tool `spotify_get_user_profile`.

### 🚩 Milestone 2: Catalog Search, Read-Only Metadata & Basic Resources
- Build catalog search tool (`spotify_search_catalog`).
- Build artist & album lookup tools (`spotify_get_artist`, `spotify_get_album`).
- Build user top items & recent history tools (`spotify_get_top_tracks`, `spotify_get_top_artists`, `spotify_get_recently_played`).
- Expose resources: `spotify://user/profile`, `spotify://user/top-tracks`, `spotify://user/top-artists`.

### 🚩 Milestone 3: Real-Time Playback & Queue Control
- Implement player control tools (`spotify_play`, `spotify_pause`, `spotify_skip_to_next`, `spotify_skip_to_previous`, `spotify_seek_to_position`, `spotify_set_volume`, `spotify_toggle_shuffle`, `spotify_set_repeat_mode`).
- Implement device transfer & state tools (`spotify_get_playback_state`, `spotify_transfer_playback`, `spotify_get_available_devices`).
- Implement queue tools (`spotify_get_queue`, `spotify_add_to_queue`).
- Expose real-time resources: `spotify://player/current`, `spotify://player/queue`.

### 🚩 Milestone 4: Full Playlist Management & Custom Cover Art
- Implement playlist CRUD tools (`spotify_create_playlist`, `spotify_get_user_playlists`, `spotify_get_playlist_items`, `spotify_add_tracks_to_playlist`, `spotify_remove_tracks_from_playlist`, `spotify_reorder_playlist_tracks`).
- Implement cover image upload (`spotify_upload_playlist_cover`).
- Expose resource scheme: `spotify://playlist/{playlist_id}`.

### 🚩 Milestone 5: Audio Features, Recommendations & Built-in Prompts
- Implement audio feature & analysis tools (`spotify_get_audio_features`, `spotify_get_audio_analysis`).
- Implement recommendation curation tool (`spotify_get_recommendations`).
- Implement built-in MCP prompts (`create_mood_playlist`, `smart_queue_dj`, `listening_dna_report`, `playlist_cleaner_and_organizer`).
- Integrate with `src/llm` provider switcher for optional native LLM execution.

### 🚩 Milestone 6: Server Packaging, Transports & Client Integration
- Standard STDIO & HTTP/SSE MCP server launcher (`python -m src.mcp_server`).
- Generate client configuration guides (`claude_desktop_config.json`, `.cursor/mcp.json`).
- End-to-end integration tests & final documentation.
