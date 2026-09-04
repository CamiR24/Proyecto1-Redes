import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "mcp.log"


class McpLogger:
    """Logs MCP requests and responses to console and to logs/mcp.log."""

    def __init__(self, log_file: Path = LOG_FILE):
        self.log_file = log_file

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _write(self, text: str):
        print(text)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def log_request(self, server: str, tool: str, arguments: dict):
        ts = self._timestamp()
        block = (
            f"\n[{ts}] MCP REQUEST\n"
            f"Server: {server}\n"
            f"Tool: {tool}\n\n"
            f"Arguments:\n{json.dumps(arguments, indent=4, ensure_ascii=False)}\n"
        )
        self._write(block)

    def log_response(self, server: str, tool: str, status: str, result):
        ts = self._timestamp()
        result_str = result if isinstance(result, str) else json.dumps(
            result, indent=4, ensure_ascii=False
        )
        block = (
            f"\n[{ts}] MCP RESPONSE\n"
            f"Server: {server}\n"
            f"Tool: {tool}\n"
            f"Status: {status}\n\n"
            f"Result:\n{result_str}\n"
        )
        self._write(block)