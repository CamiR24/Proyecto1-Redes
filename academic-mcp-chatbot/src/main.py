import asyncio
import os
from dotenv import load_dotenv
from chatbot.llm_client import LLMClient
from mcp_local.client_manager import McpClientManager

load_dotenv()


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(
            f"La variable de entorno {name} no está definida. Revisa tu archivo .env."
        )
    return value


async def run_conversation_turn(llm, mcp_manager, conversation_history):
    """Envía el historial al LLM y resuelve cualquier tool_use, hasta
    obtener una respuesta final de texto."""
    while True:
        response = llm.send_message(conversation_history, tools=mcp_manager.available_tools)

        for block in response.content:
            if block.type == "text" and block.text:
                print(f"\nAssistant > {block.text}")

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
    print("=" * 40)
    print("      Academic AI Assistant")
    print("=" * 40)

    llm = LLMClient()
    mcp_manager = McpClientManager()

    # Filesystem MCP (official)
    sandbox_path = get_required_env("MCP_SANDBOX_PATH")
    await mcp_manager.connect_to_server(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", sandbox_path],
    )

    # Git MCP (official)
    await mcp_manager.connect_to_server(
        name="git",
        command="python",
        args=["-m", "mcp_server_git"],
    )

    # Academic Planner MCP (own server)
    academic_planner_path = get_required_env("ACADEMIC_PLANNER_PATH")
    await mcp_manager.connect_to_server(
        name="academic_planner",
        command="python",
        args=["-m", "src.server"],
        cwd=academic_planner_path,
    )

    # Remote MCP (Cloud Run)
    remote_url = get_required_env("REMOTE_MCP_URL")
    await mcp_manager.connect_to_remote_server(
        name="remote_study_tips",
        url=remote_url,
    )

    # HR Management MCP (classmate: NESHGP04)
    hr_path = get_required_env("HR_SERVER_PATH")
    await mcp_manager.connect_to_server(
        name="hr_construccion",
        command=f"{hr_path}/.venv/bin/python",
        args=[f"{hr_path}/server.py"],
    )

    # Hotel Operations MCP (classmate: JosFer720)
    hotel_path = get_required_env("HOTEL_SERVER_PATH")
    await mcp_manager.connect_to_server(
        name="hotel",
        command=f"{hotel_path}/.venv/bin/python",
        args=["-m", "hotel_mcp"],
        cwd=hotel_path,
        env={**os.environ, "PYTHONPATH": "src"},
    )

    print(f"\n[MCP] Tools disponibles: {[t['name'] for t in mcp_manager.available_tools]}")

    conversation_history = []

    try:
        while True:
            user_input = input("\nYou > ").strip()

            if user_input.lower() in ("exit", "quit", "salir"):
                print("¡Hasta luego!")
                break
            if not user_input:
                continue

            conversation_history.append({"role": "user", "content": user_input})

            try:
                await run_conversation_turn(llm, mcp_manager, conversation_history)
            except Exception as e:
                print(f"\n[Error]: {e}")
                conversation_history.pop()
    finally:
        await mcp_manager.close()


if __name__ == "__main__":
    asyncio.run(main())