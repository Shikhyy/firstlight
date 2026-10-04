from abc import ABC, abstractmethod

from pydantic import BaseModel


class RawItem(BaseModel):
    source: str
    title: str
    url: str
    raw: dict
    deadline_text: str | None = None
    start_text: str | None = None
    description: str | None = None


class Connector(ABC):
    name: str
    refresh_hours: int = 24
    timeout_s: int = 20

    @abstractmethod
    def fetch(self) -> list[RawItem]: ...
