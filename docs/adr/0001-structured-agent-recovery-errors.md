# Structured JSON Responses with Self-Healing Guidance for Player Errors

When Spotify player endpoints fail due to inactive devices (HTTP 404) or account restrictions (HTTP 403), player tools catch the HTTP status and return structured JSON with actionable recovery advice instead of raising unhandled exceptions. This enables autonomous LLM agents to detect inactive devices and self-heal by calling `spotify_get_available_devices` and `spotify_transfer_playback`.
