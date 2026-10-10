# scrapers/base.py
from abc import ABC, abstractmethod
from backend.src.schemas.scrapers import RawPost

class BaseScraperPlugin(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    async def fetch(self) -> list[RawPost]:
        pass
