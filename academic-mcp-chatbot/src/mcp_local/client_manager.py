from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class McpClientManager:
    """Maneja las conexiones a uno o más servidores MCP y expone sus tools."""

    def __init__(self):
        self.sessions: dict[str, ClientSession] = {}
        self.tool_to_server: dict[str, str] = {}
        self.available_tools: list[dict] = []  #formato esperado por la API de Claude
        self._exit_stack = AsyncExitStack()

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
            self.available_tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            })

    async def call_tool(self, tool_name: str, arguments: dict):
        server_name = self.tool_to_server[tool_name]
        session = self.sessions[server_name]
        return await session.call_tool(tool_name, arguments)

    async def close(self):
        await self._exit_stack.aclose()