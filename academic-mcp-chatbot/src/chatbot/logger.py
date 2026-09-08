import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "mcp.log"

console = Console()


class McpLogger:
    """Logs MCP requests and responses: styled panels to the console,
    plain text (unchanged format) to logs/mcp.log."""

    def __init__(self, log_file: Path = LOG_FILE):
        self.log_file = log_file

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _write_to_file(self, text: str):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def log_request(self, server: str, tool: str, arguments: dict):
        ts = self._timestamp()

        # Plain text file log (unchanged format, so old logs stay consistent)
        plain = (
            f"\n[{ts}] MCP REQUEST\n"
            f"Server: {server}\n"
            f"Tool: {tool}\n\n"
            f"Arguments:\n{json.dumps(arguments, indent=4, ensure_ascii=False)}\n"
        )
        self._write_to_file(plain)

        # Styled console output
        args_json = json.dumps(arguments, indent=2, ensure_ascii=False)
        body = f"[bold]{tool}[/bold] en [italic]{server}[/italic]\n\n{args_json}"
        console.print(
            Panel(body, title=f"→ MCP REQUEST  [{ts}]", border_style="grey50", expand=False)
        )

    def log_response(self, server: str, tool: str, status: str, result):
        ts = self._timestamp()
        result_str = result if isinstance(result, str) else json.dumps(
            result, indent=4, ensure_ascii=False
        )

        plain = (
            f"\n[{ts}] MCP RESPONSE\n"
            f"Server: {server}\n"
            f"Tool: {tool}\n"
            f"Status: {status}\n\n"
            f"Result:\n{result_str}\n"
        )
        self._write_to_file(plain)

        color = "green" if status == "success" else "red"
        icon = "✅" if status == "success" else "❌"
        display_result = (
            result_str if len(result_str) < 600
            else result_str[:600] + "\n... (truncado, ver logs/mcp.log)"
        )
        body = (
            f"[bold]{tool}[/bold] en [italic]{server}[/italic] "
            f"— status: [{color}]{status}[/{color}]\n\n{display_result}"
        )
        console.print(
            Panel(body, title=f"{icon} MCP RESPONSE  [{ts}]", border_style=color, expand=False)
        )