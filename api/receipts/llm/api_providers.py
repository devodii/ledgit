from receipts.connectors.http import HttpClient
from receipts.llm.base import LLMError, LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str, api_key: str, max_tokens: int) -> None:
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.http = HttpClient(
            name="anthropic", allowed_domains=["api.anthropic.com"], rate_limit_rps=2
        )

    def complete(self, system: str, prompt: str) -> str:
        response = self.http.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
            json_body={
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        if response.status != 200:
            raise LLMError(f"anthropic returned {response.status}: {response.text[:200]}")
        blocks = response.data().get("content", [])
        return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, model: str, api_key: str, max_tokens: int) -> None:
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.http = HttpClient(name="openai", allowed_domains=["api.openai.com"], rate_limit_rps=2)

    def complete(self, system: str, prompt: str) -> str:
        response = self.http.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"authorization": f"Bearer {self.api_key}"},
            json_body={
                "model": self.model,
                "max_completion_tokens": self.max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        if response.status != 200:
            raise LLMError(f"openai returned {response.status}: {response.text[:200]}")
        return str(response.data()["choices"][0]["message"]["content"])
