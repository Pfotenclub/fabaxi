import logging
import os
from contextlib import asynccontextmanager
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, BigInteger, insert, select, delete, update

Base = declarative_base()
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.StreamHandler()])

class BirthdayTable(Base):
    __tablename__ = "birthdays"
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer, nullable=True)

class Database:
    def __init__(self):
        db_url = f"mysql+aiomysql://{os.getenv('DB_USER')}:{os.getenv('DB_PW')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.engine = create_async_engine(db_url, future=True, echo=False)
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
    
    async def get_user_record(self, user_id, guild_id):
        async with self.get_session() as session:
            record = await session.execute(
                select(BirthdayTable)
                .where(BirthdayTable.user_id == user_id, BirthdayTable.guild_id == guild_id)
            )
            return record.scalars().first()
    async def get_users_with_birthday(self, day, month):
        async with self.get_session() as session:
            records = await session.execute(
                select(BirthdayTable)
                .where(BirthdayTable.day == day, BirthdayTable.month == month)
            )
            return records.scalars().all()

    async def create_user_record(self, user_id, guild_id, birthday: date):
        async with self.get_session() as session:
            await session.execute(
                insert(BirthdayTable)
                .values(user_id=user_id, guild_id=guild_id, day=birthday.day, month=birthday.month, year=birthday.year)
            )
            await session.commit()
    async def edit_user_record(self, user_id, guild_id, birthday: date):
        async with self.get_session() as session:
            await session.execute(
                update(BirthdayTable)
                .where(BirthdayTable.user_id == user_id, BirthdayTable.guild_id == guild_id)
                .values(day=birthday.day, month=birthday.month, year=birthday.year)
            )
            await session.commit()