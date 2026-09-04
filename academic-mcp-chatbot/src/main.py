from chatbot.llm_client import LLMClient


def main():
    print("=" * 40)
    print("      Academic AI Assistant")
    print("=" * 40)

    llm = LLMClient()

    while True:
        user_input = input("\nYou > ").strip()

        if user_input.lower() in ("exit", "quit", "salir"):
            print("¡Hasta luego!")
            break

        if not user_input:
            continue

        messages = [{"role": "user", "content": user_input}]

        try:
            reply = llm.send_message(messages)
            print(f"\nAssistant > {reply}")
        except Exception as e:
            print(f"\n[Error al contactar al LLM]: {e}")


if __name__ == "__main__":
    main()