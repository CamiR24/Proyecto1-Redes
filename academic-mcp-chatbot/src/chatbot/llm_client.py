import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Wrapper around the Anthropic API client."""

    def __init__(self, model: str = "claude-sonnet-5", max_tokens: int = 1024):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY no está definida. Revisa tu archivo .env."
            )

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def send_message(self, messages: list[dict]) -> str:
        """
        Sends a list of messages to the LLM and returns the text response.
        messages: list of {"role": "user"|"assistant", "content": str}
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
        )

        # response.content is a list of blocks (text, tool_use, etc.)
        text_blocks = [block.text for block in response.content if block.type == "text"]
        return "".join(text_blocks)