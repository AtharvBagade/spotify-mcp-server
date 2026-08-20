# High-Signal Context Pruning for Ambient Resources and Player Tools

## Context
Raw Spotify API playback responses contain verbose arrays (such as `available_markets` with 180+ ISO country codes per track, duplicate URLs, and album copyright arrays). Exposing these directly via MCP ambient resources (`spotify://player/current`, `spotify://player/queue`) and tool outputs significantly bloats LLM token contexts without providing actionable information.

## Decision
All playback, queue, and device tools/resources prune low-signal verbose fields and return curated, structured JSON objects:
- **Preserved**: Track name, artist names, album name, duration (`duration_ms`), progress (`progress_ms`), track URI, device name/type/volume/status, shuffle state, and repeat state.
- **Pruned**: `available_markets`, track preview URLs, external IDs (ISRC/EAN), and nested album copyright arrays.

## Consequences
Reduces token payload size by over 80% while retaining all essential context for LLM decision-making and tool reasoning.
