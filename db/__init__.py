import os
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()


class Database:
    def __init__(self):
        db_url = f"mysql+aiomysql://{os.getenv('DB_USER')}:{os.getenv('DB_PW')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.engine = create_async_engine(db_url, pool_recycle=3600, pool_pre_ping=True, pool_use_lifo=True)
        self.SessionLocal = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self):
        async with self.SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
