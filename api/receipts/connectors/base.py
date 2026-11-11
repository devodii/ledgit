from abc import ABC, abstractmethod
from typing import ClassVar

from pydantic import BaseModel


class HealthResult(BaseModel):
    connector: str
    ok: bool
    detail: str


class Connector(ABC):
    name: ClassVar[str]
    allowed_domains: ClassVar[list[str]]
    rate_limit_rps: ClassVar[float]
    emits: ClassVar[list[str]]

    @abstractmethod
    def healthcheck(self) -> HealthResult: ...
