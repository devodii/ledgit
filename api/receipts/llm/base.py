from abc import ABC, abstractmethod


class LLMError(Exception):
    pass


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def complete(self, system: str, prompt: str) -> str: ...
