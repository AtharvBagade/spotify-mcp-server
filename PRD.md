# Product Requirements Document (PRD)

## Project Name: **TasteMatch AI**

### Subtitle: Open-Source AI Playlist Generation Engine & MCP Service Layer

---

### 1. Executive Summary & Core Objective

**TasteMatch AI** is a lightweight, self-hostable service designed to act as an open-source alternative to proprietary "AI Playlist" tools. The absolute goal of this service is to translate natural language user prompts and environmental concepts into highly tailored, structured Spotify playlists.

Rather than functioning as a closed black box, TasteMatch AI operates as a unified **music utility layer**. It exposes its capabilities through a local companion interface and natively as a **Model Context Protocol (MCP) server**. This design enables standard human interactions via a minimal dashboard while allowing external AI clients (e.g., Claude Desktop, Cursor, standalone agents) to programmatically analyze a user's library and manipulate playlists directly through their own chat contexts.

---

### 2. System Entry Points & Interaction Models

The application completely decouples the operational interface from the core pipeline logic, serving users and developer agents through two distinct operational vectors:

#### 📊 Entry Point A: The Local Dashboard

A minimalist, single-page client running locally on the user's host machine. Built for fast manual curation, visual parameter tweaking, and initial authentication setups.

* Local-first API Key configuration inputs.
* Direct text prompt execution box.
* Granular filtering slider arrays.

#### 🤖 Entry Point B: The MCP Server Portal

Exposes the local running service instance to any Model Context Protocol compliant application, giving external LLMs native tool capability over the music layer.

* Allows LLMs to scan the user's track history.
* Allows direct creation commands via chat prompts.
* Ideal for terminal tools and developer workflows.

---

### 3. Flexible Large Language Model (LLM) Integration

TasteMatch AI does not hardcode its natural language processing pipeline to a specific vendor. The architecture relies on structural parameter parsing that can be handled interchangeably by providing one of the following local or cloud options:

* **Commercial API Connectors:** Direct native support for developer keys from Google Gemini, Anthropic Claude, or OpenAI. All keys are injected directly into environment files locally or typed via the UI and are never passed to an intermediary service.
* **Local Host Infrastructure:** Complete compatibility with local inference engines running via Ollama or LocalAI (e.g., mapping to local instances of `llama3` or `mistral`) using an editable base URL configuration endpoint, ensuring zero financial cost for high-volume execution.

---

### 4. Core Functional Feature Scopes

#### 4.1 Generation Curation Strategies

To provide deeper granularity than commercial streaming features, generation pipelines can be locked into three explicit strategy profiles depending on user requirements:

| Strategy Profile | Mechanic Overview | Primary Operational Target |
| --- | --- | --- |
| **The Closed Sandbox** | Constrains the pipeline exclusively to search, filter, and extract items matching the target vibe from within the user's own Liked Songs collection or designated source folders. | Intelligent internal library parsing and deep filtering. |
| **The Hybrid Bridge** | Uses the user's current music history and top tracks as core seed anchors, but actively injects a controlled variable layer (20-40%) of discovery candidates fetched directly from the external streaming ecosystem. | Context-guided music discovery with a high success baseline. |
| **The Wild Card** | Instructs the pipeline to completely disregard the user's library and create an isolated sonic landscape drawn entirely from the LLM's interpretation of the concepts. | Concept playlists, specific eras, and non-biased exploration. |

#### 4.2 Unified Exclusion Matrix (Global Blacklists)

The system enforces a persistent JSON configuration matrix that acts as a strict guardrail before any playlist curation is deployed to a streaming account. The curation pipeline must crosscheck this configuration block and instantly prune out matching candidates:

* `artists`: Array of immutable system Artist IDs that are prohibited from entering generated tracklists.
* `tracks`: Specific Track IDs to permanently omit from automated curation.
* `genres`: String flags that filter out associated tracks based on underlying tag matching.

---

### 5. MCP Specification (Agent Tool Definitions)

To enable AI agents to orchestrate operations out of the box, the server exposes the following exact json-schema tool signatures to the client context:

```json
{
  "tools": [
    {
      "name": "get_liked_tracks_metadata",
      "description": "Retrieves high-level metadata of a user's liked library tracks to capture their taste signature.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "limit": { "type": "number", "description": "Number of recent items to parse" }
        }
      }
    },
    {
      "name": "search_spotify_catalog",
      "description": "Searches the global streaming catalog for track matches based on concept queries and structural tags.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": { "type": "string" },
          "type": { "type": "string", "enum": ["track", "artist"] }
        },
        "required": ["query"]
      }
    },
    {
      "name": "create_ai_playlist",
      "description": "Compiles a final validated list of track URIs and writes it as a fresh playlist to the user account.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "name": { "type": "string", "description": "The title of the playlist" },
          "trackUris": { 
            "type": "array", 
            "items": { "type": "string" },
            "description": "Array of unique tracking strings"
          },
          "description": { "type": "string" }
        },
        "required": ["name", "trackUris"]
      }
    }
  ]
}

```

---

### 6. Initial Configuration Setup

> **Minimum Boot Requirements:** To kick off development workflows or let an AI agent initiate boilerplate scaffolding, the host system requires a local root environment file built exactly as follows:

```env
# Core Integration Credentials
SPOTIFY_CLIENT_ID="your_spotify_client_id_here"
SPOTIFY_CLIENT_SECRET="your_spotify_client_secret_here"
SPOTIFY_REDIRECT_URI="http://localhost:3000/auth/callback"

# LLM Gateway Target Toggles
LLM_PROVIDER="openai" # Toggles between: openai | gemini | claude | local
LLM_API_KEY="your_active_llm_api_key_or_empty_for_local"
LOCAL_LLM_BASE_URL="http://localhost:11434/v1" # Target mapping path for Ollama

```
