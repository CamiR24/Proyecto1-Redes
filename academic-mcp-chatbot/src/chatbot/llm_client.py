import os
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import date

load_dotenv()


class LLMClient:
    def __init__(self, model: str = "claude-sonnet-5", max_tokens: int = 1024):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY no está definida. Revisa tu archivo .env."
            )
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def send_message(self, messages: list[dict], tools: list[dict] | None = None):
        """Devuelve el objeto de respuesta completo (no solo texto), ya que
        necesitamos inspeccionar tool_use blocks."""
        kwargs = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            system=f"La fecha de hoy es {date.today().isoformat()}. "
                f"Úsala como referencia para interpretar fechas relativas o incompletas "
                f"que mencione el usuario (ej. asumir el año actual si no lo especifica).",
            messages=messages,
        )
        if tools:
            kwargs["tools"] = tools
        return self.client.messages.create(**kwargs)