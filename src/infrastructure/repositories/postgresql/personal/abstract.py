from abc import ABC, abstractmethod
from typing import List


class AbstractPersonalRepository(ABC):
    @abstractmethod
    async def find_by_embedding(self, embedding: List[float]):
        raise NotImplementedError()