from receipts.llm.api_providers import AnthropicProvider, OpenAIProvider
from receipts.llm.base import LLMError, LLMProvider
from receipts.llm.claude_code import ClaudeCodeProvider
from receipts.llm.fake import FakeProvider
from receipts.settings import Settings, get_settings


def get_provider(settings: Settings | None = None) -> LLMProvider:
    settings = settings or get_settings()
    match settings.llm_provider:
        case "claude_code":
            return ClaudeCodeProvider(settings.llm_model)
        case "anthropic":
            return AnthropicProvider(
                settings.llm_model, settings.llm_api_key, settings.llm_max_tokens
            )
        case "openai":
            return OpenAIProvider(settings.llm_model, settings.llm_api_key, settings.llm_max_tokens)
        case _:
            return FakeProvider()


__all__ = ["LLMError", "LLMProvider", "FakeProvider", "ClaudeCodeProvider", "get_provider"]
