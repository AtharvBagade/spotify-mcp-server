# TasteMatch AI - Unified LLM Switcher & Playlist Engine

TasteMatch AI is an open-source AI playlist generation engine and MCP service layer.

## Milestone 1: Unified LLM Provider Switcher

TasteMatch AI includes a native provider switcher allowing seamless hot-swapping between **OpenAI**, **Anthropic Claude**, **Ollama** (Local), and **Google Gemini**.

### Features
* **Multi-Provider Architecture**: Hot-swap between OpenAI, Claude, Ollama, and Gemini at runtime.
* **Unified Interface**: Standardized response format (`LLMResponse`) and structured Pydantic schema extraction across all providers via `litellm`.
* **Automatic Fallback**: Fall back to secondary configured providers if primary provider encounters errors or rate limits.
* **Multi-Provider Diagnostics**: Built-in health checker to ping and measure latency across all 4 providers.
* **Rich Terminal CLI**: Interactive CLI dashboard to test prompts and switch providers on the fly.

### Environment Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in your API keys in `.env`:
   ```env
   LLM_PROVIDER="openai"
   OPENAI_API_KEY="sk-..."
   ANTHROPIC_API_KEY="sk-ant-..."
   GEMINI_API_KEY="AIzaSy..."
   LOCAL_LLM_BASE_URL="http://localhost:11434"
   ```

### Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running the Interactive Switcher CLI
```bash
python3 main.py
```

### Running Tests
```bash
pytest
```
