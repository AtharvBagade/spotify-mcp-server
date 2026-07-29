#!/usr/bin/env python3
"""TasteMatch AI - Unified LLM Provider Switcher CLI Dashboard."""

import sys
from typing import Optional
from pydantic import BaseModel, Field

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from src.config import LLMSettings, load_settings
from src.llm.models import LLMProviderEnum, LLMResponse
from src.llm.service import LLMService
from src.llm.health import LLMHealthChecker

console = Console()


class SamplePlaylistRecommendation(BaseModel):
    """Sample structured output schema for playlist generation test."""

    playlist_name: str = Field(description="Catchy title for the playlist")
    genre_vibe: str = Field(description="Primary musical aesthetic or genre")
    vibe_description: str = Field(description="Detailed atmospheric description")
    recommended_tracks: list[str] = Field(
        description="List of 3-5 track titles with artist names"
    )


def display_header():
    """Render top banner header."""
    header_text = (
        "[bold cyan]TasteMatch AI[/bold cyan] - [bold magenta]Unified LLM Provider Gateway[/bold magenta]\n"
        "[dim]Seamlessly switch between OpenAI, Anthropic Claude, Ollama, and Google Gemini[/dim]"
    )
    console.print(Panel(header_text, border_style="cyan", expand=False))


def display_status_panel(service: LLMService):
    """Render current status table."""
    status = service.get_status()
    table = Table(
        title="[bold yellow]Current LLM Gateway Status[/bold yellow]",
        border_style="yellow",
    )
    table.add_column("Setting", style="bold cyan")
    table.add_column("Value", style="green")

    table.add_row(
        "Active Provider",
        f"[bold underline]{status['active_provider'].upper()}[/bold underline]",
    )
    table.add_row("Active Model", status["active_model"])
    table.add_row("LiteLLM Identifier", status["litellm_model_string"])
    table.add_row(
        "Auto Fallback", "Enabled" if status["fallback_enabled"] else "Disabled"
    )
    table.add_row("Local Ollama Host", status["ollama_base_url"])

    console.print(table)


def run_health_checks(health_checker: LLMHealthChecker):
    """Execute diagnostics across all 4 providers and render formatted table."""
    console.print(
        "\n[bold cyan]Running diagnostic health checks across providers...[/bold cyan]"
    )

    with console.status("[bold green]Pinging LLM providers...", spinner="dots"):
        health_results = health_checker.check_all()

    table = Table(
        title="[bold blue]Provider Diagnostic Results[/bold blue]", border_style="blue"
    )
    table.add_column("Provider", style="bold white")
    table.add_column("Default Model", style="dim white")
    table.add_column("Status", style="bold")
    table.add_column("Latency (ms)", justify="right")
    table.add_column("Diagnostic Message", style="dim")

    for provider, health in health_results.items():
        if health.is_available:
            status_str = "[bold green]✓ AVAILABLE[/bold green]"
            latency_str = f"{health.latency_ms} ms" if health.latency_ms else "N/A"
        else:
            status_str = "[bold red]✗ UNAVAILABLE[/bold red]"
            latency_str = "-"

        table.add_row(
            provider.value.upper(),
            health.model,
            status_str,
            latency_str,
            health.message,
        )

    console.print(table)


def handle_switch_provider(service: LLMService):
    """Interactive prompt for switching provider and model."""
    console.print("\n[bold yellow]Switch Active Provider[/bold yellow]")
    console.print("1. [cyan]OpenAI[/cyan] (Default: gpt-4o-mini)")
    console.print("2. [cyan]Claude[/cyan] (Default: claude-3-5-sonnet-20241022)")
    console.print("3. [cyan]Ollama[/cyan] (Default: llama3.2)")
    console.print("4. [cyan]Gemini[/cyan] (Default: gemini-1.5-flash)")

    choice = Prompt.ask(
        "Select provider number", choices=["1", "2", "3", "4"], default="1"
    )

    provider_map = {
        "1": LLMProviderEnum.OPENAI,
        "2": LLMProviderEnum.CLAUDE,
        "3": LLMProviderEnum.OLLAMA,
        "4": LLMProviderEnum.GEMINI,
    }
    selected_provider = provider_map[choice]

    custom_model = Prompt.ask(
        f"Enter model name for [bold]{selected_provider.value}[/bold] (Leave blank for default)",
        default="",
    )

    service.set_provider(
        selected_provider, model=custom_model if custom_model.strip() else None
    )
    console.print(
        f"[bold green]Successfully switched active provider to [{service.active_provider.value.upper()}] "
        f"using model [{service.active_model}]![/bold green]\n"
    )


def handle_generate_text(service: LLMService):
    """Execute arbitrary text prompt against active provider."""
    prompt_text = Prompt.ask(
        "\n[bold cyan]Enter prompt for playlist generation / LLM test[/bold cyan]",
        default="Describe the ideal atmospheric vibe for a late-night rainy drive in Tokyo.",
    )

    console.print(
        f"\n[dim]Sending prompt to [bold]{service.active_provider.value.upper()}[/bold] ({service.active_model})...[/dim]"
    )

    try:
        with console.status("[bold green]Generating response...", spinner="earth"):
            response: LLMResponse = service.generate(prompt_text)

        console.print(
            Panel(
                response.content,
                title=f"[bold green]Response from {response.provider.value.upper()} ({response.model})[/bold green]",
                border_style="green",
            )
        )
        console.print(
            f"[dim]Latency: {response.latency_ms} ms | Tokens: {response.total_tokens} (Prompt: {response.prompt_tokens}, Completion: {response.completion_tokens})[/dim]\n"
        )
    except Exception as e:
        console.print(f"[bold red]Generation Error:[/bold red] {e}\n")


def handle_structured_output_demo(service: LLMService):
    """Execute structured JSON extraction test."""
    prompt_text = Prompt.ask(
        "\n[bold cyan]Enter concept prompt for structured JSON playlist generation[/bold cyan]",
        default="Create a 4-track playlist for studying synth-wave electronic music.",
    )

    console.print(
        f"\n[dim]Requesting structured JSON from [bold]{service.active_provider.value.upper()}[/bold]...[/dim]"
    )

    try:
        with console.status(
            "[bold green]Parsing structured output schema...", spinner="bouncingBar"
        ):
            result = service.generate_structured(
                prompt_text, SamplePlaylistRecommendation
            )

        json_str = result.model_dump_json(indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        console.print(
            Panel(
                syntax,
                title="[bold green]Validated Pydantic Playlist Object[/bold green]",
                border_style="cyan",
            )
        )
    except Exception as e:
        console.print(f"[bold red]Structured Parsing Error:[/bold red] {e}\n")


def main():
    """Main CLI execution loop."""
    settings = load_settings()
    service = LLMService(settings=settings)
    health_checker = LLMHealthChecker(settings=settings)

    display_header()

    while True:
        console.print("[bold white]Main Menu:[/bold white]")
        console.print("1. [green]View Gateway Status[/green]")
        console.print("2. [cyan]Switch Active LLM Provider / Model[/cyan]")
        console.print("3. [blue]Run Multi-Provider Health Checks[/blue]")
        console.print("4. [magenta]Execute Test Text Prompt[/magenta]")
        console.print("5. [yellow]Execute Structured JSON Output Test[/yellow]")
        console.print("6. [red]Exit[/red]")

        choice = Prompt.ask(
            "Select an option", choices=["1", "2", "3", "4", "5", "6"], default="1"
        )

        if choice == "1":
            display_status_panel(service)
        elif choice == "2":
            handle_switch_provider(service)
        elif choice == "3":
            run_health_checks(health_checker)
        elif choice == "4":
            handle_generate_text(service)
        elif choice == "5":
            handle_structured_output_demo(service)
        elif choice == "6":
            console.print(
                "\n[bold cyan]Exiting TasteMatch AI LLM Switcher. Goodbye![/bold cyan]"
            )
            sys.exit(0)


if __name__ == "__main__":
    main()
