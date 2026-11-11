import json
from collections.abc import Callable

from receipts.llm.base import LLMProvider


class FakeProvider(LLMProvider):
    name = "fake"
    model = "fake-deterministic"

    def __init__(self, responder: Callable[[str, str], str] | None = None) -> None:
        self._responder = responder

    def complete(self, system: str, prompt: str) -> str:
        if self._responder:
            return self._responder(system, prompt)
        return json.dumps({"claims": []})
