import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt

from chatbot.llm_client import LLMClient
from mcp_local.client_manager import McpClientManager

load_dotenv()
console = Console()


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(
            f"La variable de entorno {name} no está definida. Revisa tu archivo .env."
        )
    return value


def print_banner():
    console.print(
        Panel(
            "[bold cyan]🎓  Academic AI Assistant[/bold cyan]\n"
            "[dim]Chatbot con acceso a múltiples servidores MCP[/dim]",
            border_style="cyan",
        )
    )


def print_tools_summary(mcp_manager: McpClientManager):
    table = Table(title="Servidores y herramientas conectadas", show_lines=False)
    table.add_column("Servidor", style="bold cyan")
    table.add_column("Herramientas", style="white")

    by_server: dict[str, list[str]] = {}
    for tool_name, server_name in mcp_manager.tool_to_server.items():
        by_server.setdefault(server_name, []).append(tool_name)

    for server_name, tools in by_server.items():
        table.add_row(server_name, ", ".join(sorted(tools)))

    console.print(table)


async def run_conversation_turn(llm, mcp_manager, conversation_history):
    """Envía el historial al LLM y resuelve cualquier tool_use, hasta
    obtener una respuesta final de texto."""
    while True:
        with console.status("[bold cyan]Pensando...[/bold cyan]", spinner="dots"):
            response = llm.send_message(conversation_history, tools=mcp_manager.available_tools)

        for block in response.content:
            if block.type == "text" and block.text:
                console.print(
                    Panel(
                        Markdown(block.text),
                        title="🎓 Assistant",
                        border_style="green",
                        expand=False,
                    )
                )

        conversation_history.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = await mcp_manager.call_tool(block.name, block.input)
                result_text = "".join(
                    c.text for c in result.content if hasattr(c, "text")
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                })

        conversation_history.append({"role": "user", "content": tool_results})


async def main():
    print_banner()

    llm = LLMClient()
    mcp_manager = McpClientManager()

    with console.status("[dim]Conectando servidores MCP...[/dim]"):
        sandbox_path = get_required_env("MCP_SANDBOX_PATH")
        await mcp_manager.connect_to_server(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", sandbox_path],
        )

        await mcp_manager.connect_to_server(
            name="git",
            command="python",
            args=["-m", "mcp_server_git"],
        )

        academic_planner_path = get_required_env("ACADEMIC_PLANNER_PATH")
        await mcp_manager.connect_to_server(
            name="academic_planner",
            command="python",
            args=["-m", "src.server"],
            cwd=academic_planner_path,
        )

        remote_url = get_required_env("REMOTE_MCP_URL")
        await mcp_manager.connect_to_remote_server(
            name="remote_study_tips",
            url=remote_url,
        )

        hr_path = get_required_env("HR_SERVER_PATH")
        await mcp_manager.connect_to_server(
            name="hr_construccion",
            command=f"{hr_path}/.venv/bin/python",
            args=[f"{hr_path}/server.py"],
        )

        hotel_path = get_required_env("HOTEL_SERVER_PATH")
        await mcp_manager.connect_to_server(
            name="hotel",
            command=f"{hotel_path}/.venv/bin/python",
            args=["-m", "hotel_mcp"],
            cwd=hotel_path,
            env={**os.environ, "PYTHONPATH": "src"},
        )

    print_tools_summary(mcp_manager)
    console.print("[dim]Escribe 'exit', 'quit' o 'salir' para terminar.[/dim]\n")

    conversation_history = []

    try:
        while True:
            user_input = Prompt.ask("[bold green]You[/bold green]").strip()

            if user_input.lower() in ("exit", "quit", "salir"):
                console.print("[dim]¡Hasta luego![/dim]")
                break
            if not user_input:
                continue

            conversation_history.append({"role": "user", "content": user_input})

            try:
                await run_conversation_turn(llm, mcp_manager, conversation_history)
            except Exception as e:
                console.print(Panel(f"[red]{e}[/red]", title="❌ Error", border_style="red"))
                conversation_history.pop()
    finally:
        await mcp_manager.close()


if __name__ == "__main__":
    asyncio.run(main())