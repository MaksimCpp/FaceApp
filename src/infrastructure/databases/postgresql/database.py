from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    async_sessionmaker, create_async_engine
)

from settings import settings

Base = declarative_base()
engine = create_async_engine(
    settings.database.get_database_url()
)
sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)

async def create_tables(engine):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
