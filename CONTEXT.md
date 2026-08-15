# Spotify MCP Server

The Spotify MCP Server exposes Spotify Web API capabilities to LLMs via Model Context Protocol (MCP) tools, ambient resources, and multi-step prompt templates.

## Language

**Player**:
The active Spotify playback session associated with a user account and target device.
_Avoid_: Audio engine, media player

**Playback State**:
The real-time status of playback including active device, track progression, shuffle, and repeat modes.
_Avoid_: Player status, player info

**Device**:
An active or available Spotify Connect client (desktop, web player, mobile, smart speaker) identified by a unique device ID.
_Avoid_: Client, speaker, endpoint

**Queue**:
The ordered list of upcoming tracks scheduled to play after the current track.
_Avoid_: Up next list, playlist buffer

**Context URI**:
A Spotify URI identifying an album, artist, or playlist context used to initiate sequential playback.
_Avoid_: Container link, playlist ID string

**High-Signal Resource**:
A pruned representation of a Spotify API entity optimized for LLM context windows, omitting verbose arrays (e.g. `available_markets`, redundant URLs, copyrights).
_Avoid_: Raw payload, trimmed dump

## Flagged Ambiguities

- **Device vs. Player**: A *Device* is a physical or virtual Spotify Connect hardware client, whereas the *Player* represents the active playback session running on a selected device.
- **Context URI vs. Track URIs in Playback**: A *Context URI* initiates playback of a container (album, artist, playlist), whereas *Track URIs* specifies an explicit sequence of individual songs. Spotify prohibits providing both simultaneously.

## Example Dialogue

> **Developer**: "The user requested ambient playback context. Should we return the full API response?"
>
> **Domain Expert**: "No, format it as a **High-Signal Resource**. Prune verbose metadata like `available_markets` and keep the active **Device**, **Playback State**, and current track details."
>
> **Developer**: "Understood. If no **Device** is active when the user asks to start playback, how do we proceed?"
>
> **Domain Expert**: "The tool returns a structured error instructing the agent to inspect available **Devices** and transfer the **Player** before retrying."
