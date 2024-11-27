from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, BigInteger, insert, select, delete

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
    def __init__(self, db_url="sqlite+aiosqlite:///./../data/karma.db"):
        self.engine = create_async_engine(db_url, future=True, echo=True)
        self.SessionLocal = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def init_db(self):
        """Create all tables in the database."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self):
        """Provide an async session."""
        async with self.SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()



    async def create_user_record_in_karma(self, user_id, guild_id):
        async with self.get_session() as session:
            insert_stmt = insert(KarmaTable).values(
                user_id=user_id,
                guild_id=guild_id,
                karma=0
            )
            await session.execute(insert_stmt)


    async def adjust_karma_for_user(self, user_id, guild_id, amount: int):
        async with self.get_session() as session:
            record = await session.get(KarmaTable, {"user_id": user_id, "guild_id": guild_id})

            if record:
                record.karma += amount
            else:
                record = KarmaTable(user_id=user_id, guild_id=guild_id, karma=+amount)
                session.add(record)

            await session.commit()

    async def get_karma_leaderboard(self, guild_id, limit:int=10):
        async with self.get_session() as session:
            result = await session.execute(
                select(KarmaTable)
                .where(KarmaTable.guild_id == guild_id)
                .order_by(KarmaTable.karma.desc())
                .limit(limit)
            )
            return result.scalars().all()

    async def clear_karma_leaderboard(self, guild_id):
        async with self.get_session() as session:
            await session.execute(delete(KarmaTable).where(KarmaTable.guild_id == guild_id))
            await session.commit()

    async def get_user_karma(self, user_id, guild_id):
        async with self.get_session() as session:
            record = await session.get(KarmaTable, {"user_id": user_id, "guild_id": guild_id})
            return record.karma if record else 0

    async def adjust_karma_for_user(self, user_id, guild_id, amount: int):
        async with self.get_session() as session:
            record = await session.get(KarmaTable, {"user_id": user_id, "guild_id": guild_id})
            if record:
                record.karma += amount
            else:
                record = KarmaTable(user_id=user_id, guild_id=guild_id, karma=amount)
                session.add(record)
            await session.commit()

    async def add_reward(self, role_id, guild_id, karma_needed: int):
        async with self.get_session() as session:
            reward = RewardsTable(role_id=role_id, guild_id=guild_id, karma_needed=karma_needed)
            session.add(reward)
            await session.commit()

    async def remove_reward(self, role_id, guild_id):
        async with self.get_session() as session:
            reward = await session.get(RewardsTable, {"role_id": role_id, "guild_id": guild_id})
            if reward:
                await session.delete(reward)
                await session.commit()

    async def list_rewards(self, guild_id):
        async with self.get_session() as session:
            result = await session.execute(
                select(RewardsTable).where(RewardsTable.guild_id == guild_id)
            )
            return result.scalars().all()