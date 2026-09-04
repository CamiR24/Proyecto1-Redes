from chatbot.llm_client import LLMClient


def main():
    print("=" * 40)
    print("      Academic AI Assistant")
    print("=" * 40)

    llm = LLMClient()
    conversation_history = []  #guarda historial 

    while True:
        user_input = input("\nYou > ").strip()

        if user_input.lower() in ("exit", "quit", "salir"):
            print("¡Hasta luego!")
            break

        if not user_input:
            continue

        # Agregamos el mensaje del usuario al historial
        conversation_history.append({"role": "user", "content": user_input})

        try:
            reply = llm.send_message(conversation_history)
            print(f"\nAssistant > {reply}")

            # Agregamos la respuesta del modelo al historial también
            conversation_history.append({"role": "assistant", "content": reply})

        except Exception as e:
            print(f"\n[Error al contactar al LLM]: {e}")
            # Si falló, no dejamos el mensaje del usuario "colgado" en el historial
            conversation_history.pop()


if __name__ == "__main__":
    main()