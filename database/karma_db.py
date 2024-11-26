from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, BigInteger

Base = declarative_base()

class KarmaTable(Base):
    __tablename__ = "karma"
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    karma = Column(Integer, default=0)
    timestamp_last_message = Column(Integer, default=0)


class RewardsTable(Base):
    __tablename__ = "rewards"
    role_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    karma_needed = Column(Integer, nullable=False)

class Database:
    def __init__(self, db_url="sqlite+aiosqlite:///./data/karma.db"):
        self.engine = create_async_engine(db_url, future=True, echo=True)
        self.SessionLocal = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def init_db(self):
        """Create all tables in the database."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self):
        """Provide an async session."""
        return self.SessionLocal()