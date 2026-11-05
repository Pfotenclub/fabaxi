from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PW

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        db_url = URL.create(
            drivername="mysql+aiomysql",
            username=DB_USER,
            password=DB_PW,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
        )
        _engine = create_async_engine(db_url, pool_recycle=3600, pool_pre_ping=True, pool_use_lifo=True)
        _SessionLocal = sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine


def get_session_maker():
    global _SessionLocal
    if _SessionLocal is None:
        get_engine()
    return _SessionLocal


class Database:
    @property
    def engine(self):
        return get_engine()

    @property
    def SessionLocal(self):
        return get_session_maker()

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def ping(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    @asynccontextmanager
    async def get_session(self):
        async with self.SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
