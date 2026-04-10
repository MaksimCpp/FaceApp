from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.personal.models import PersonalDTO
from infrastructure.repositories.postgresql.personal.abstract import AbstractPersonalRepository
from infrastructure.databases.postgresql.models import Personal


class PostgreSQLPersonalRepository(AbstractPersonalRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def find_by_embedding(self, embedding: List[float]):
        query = select(
            Personal
        ).where(
            (1 - Personal.embedding.cosine_distance(embedding)) > 0.5
        ).order_by(
            Personal.embedding.cosine_distance(embedding)
        ).limit(1)

        result = await self._session.execute(query)
        personal = result.scalar_one_or_none()

        if personal is None:
            return None
        
        return PersonalDTO(
            id=personal.id,
            full_name=personal.full_name,
            embedding=personal.embedding
        )
    