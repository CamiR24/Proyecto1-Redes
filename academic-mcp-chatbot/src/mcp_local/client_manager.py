from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from chatbot.logger import McpLogger


class McpClientManager:
    """Maneja las conexiones a uno o más servidores MCP y expone sus tools."""

    def __init__(self):
        self.sessions: dict[str, ClientSession] = {}
        self.tool_to_server: dict[str, str] = {}
        self.available_tools: list[dict] = []  #formato esperado por la API de Claude
        self._exit_stack = AsyncExitStack()
        self.logger = McpLogger() 

    async def connect_to_server(self, name: str, command: str, args: list[str]):
        server_params = StdioServerParameters(command=command, args=args)

        stdio, write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        session = await self._exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        await session.initialize()
        self.sessions[name] = session

        response = await session.list_tools()
        for tool in response.tools:
            self.tool_to_server[tool.name] = name
            schema = getattr(tool, "input_schema", None) or getattr(tool, "inputSchema", None)
            self.available_tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": schema,
            })

    async def call_tool(self, tool_name: str, arguments: dict):
        server_name = self.tool_to_server[tool_name]
        session = self.sessions[server_name]

        self.logger.log_request(server_name, tool_name, arguments)

        try:
            result = await session.call_tool(tool_name, arguments)
            result_text = "".join(
                c.text for c in result.content if hasattr(c, "text")
            )
            self.logger.log_response(server_name, tool_name, "success", result_text)
            return result
        except Exception as e:
            self.logger.log_response(server_name, tool_name, "error", str(e))
            raise

    async def close(self):
        await self._exit_stack.aclose()