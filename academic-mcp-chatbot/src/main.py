import asyncio
from chatbot.llm_client import LLMClient
from mcp_local.client_manager import McpClientManager


async def run_conversation_turn(llm, mcp_manager, conversation_history):
    """Envía el historial al LLM y resuelve cualquier tool_use, hasta obtener una respuesta final de texto."""
    while True:
        response = llm.send_message(conversation_history, tools=mcp_manager.available_tools)

        for block in response.content:
            if block.type == "text" and block.text:
                print(f"\nAssistant > {block.text}")

        conversation_history.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break  #respuesta final

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\n[MCP] Usando herramienta: {block.name} | args={block.input}")
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

    # IMPORTANTE: reemplaza esta ruta por la carpeta sandbox real en tu máquina
    await mcp_manager.connect_to_server(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/Users/Camila/mcp-sandbox"],
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