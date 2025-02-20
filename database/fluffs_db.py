import logging
import os
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Boolean, insert, select, delete

Base = declarative_base()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.StreamHandler()])
class MasterFluffTable(Base):
    __tablename__ = "master_fluffs"
    fluff_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    type1 = Column(String)
    type2 = Column(String, nullable=True)
    hp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)
    evolve = Column(Integer, nullable=True)
    evolve_lvl = Column(Integer, nullable=True)
    fluff_user_relation = relationship("FluffUserTable", back_populates="master_fluff_relation")

class FluffUserTable(Base):
    __tablename__ = "fluff_users"
    fluff_user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    fluff_id = Column(Integer, ForeignKey("master_fluffs.fluff_id"))
    name = Column(String)
    description = Column(String)
    type1 = Column(String)
    type2 = Column(String, nullable=True)
    level = Column(Integer)
    exp = Column(Integer)
    max_hp = Column(Integer)
    hp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)
    main = Column(Boolean, default=False)
    master_fluff_relation = relationship("MasterFluffTable", back_populates="fluff_user_relation")

class TypeTable(Base):
    __tablename__ = "types"
    # Columns are Attacking and Rows are Defending
    type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    Fire = Column(String, nullable=True)
    Water = Column(String, nullable=True)
    Grass = Column(String, nullable=True)
    Normal = Column(String, nullable=True)
    Electric = Column(String, nullable=True)
    Ground = Column(String, nullable=True)


class Database:
    def __init__(self, db_url="sqlite+aiosqlite:///./../data/fluffs.db"):
        if os.environ.get("DOCKER") is None:
            self.engine = create_async_engine(db_url, future=True, echo=False)
            #self.engine = create_async_engine(db_url, future=True, echo=True)
        else:
            self.engine = create_async_engine("sqlite+aiosqlite:////db/fluffs.db", future=True, echo=False)
            #self.engine = create_async_engine("sqlite+aiosqlite:////db/fluffs.db", future=True, echo=True)
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

    async def create_fluff_from_master(self, user_id, guild_id, fluff_id, main=False):
        async with self.get_session() as session:
            master_fluff = await self.get_master_fluff_by_id(fluff_id)
            fluff = FluffUserTable(
                user_id=user_id,
                guild_id=guild_id,
                fluff_id=fluff_id,
                name=master_fluff.name,
                description=master_fluff.description,
                type1=master_fluff.type1,
                type2=master_fluff.type2,
                level=1,
                exp=0,
                max_hp=master_fluff.hp,
                hp=master_fluff.hp,
                attack=master_fluff.attack,
                defense=master_fluff.defense,
                speed=master_fluff.speed,
                main=main
            )
            session.add(fluff)
            await session.commit()
            return fluff
    
    async def create_fluff(self, user_id, guild_id, fluff_id, name, description, type1, level, exp, hp, attack, defense, speed, type2=None, main=False):
        async with self.get_session() as session:
            fluff = FluffUserTable(
                user_id=user_id,
                guild_id=guild_id,
                fluff_id=fluff_id,
                name=name,
                description=description,
                type1=type1,
                type2=type2,
                level=level,
                exp=exp,
                max_hp=hp,
                hp=hp,
                attack=attack,
                defense=defense,
                speed=speed,
                main=main
            )
            session.add(fluff)
            await session.commit()
            return fluff

    async def get_master_fluff_by_id(self, fluff_id):
        async with self.get_session() as session:
            result = await session.execute(
                select(MasterFluffTable)
                .where(MasterFluffTable.fluff_id == fluff_id)
            )
            return result.scalars().first()
    
    async def get_fluffs_by_user(self, user_id, guild_id):
        async with self.get_session() as session:
            result = await session.execute(
                select(FluffUserTable)
                .where(FluffUserTable.user_id == user_id, FluffUserTable.guild_id == guild_id)
            )
            return result.scalars().all()

    async def get_fluff_by_id(self, fluff_id):
        async with self.get_session() as session:
            result = await session.execute(
                select(FluffUserTable)
                .where(FluffUserTable.fluff_user_id == fluff_id)
            )
            return result.scalars().first()

    async def is_effective(self, attacking_type, defending_type):
        async with self.get_session() as session:
            result = await session.execute(
                select(TypeTable)
                .where(TypeTable.name == defending_type)
            )
            type_row = result.scalars().first()
            if type_row is None:
                return ""
            return getattr(type_row, attacking_type)

    async def set_fluff_hp(self, fluff_id, hp):
        async with self.get_session() as session:
            fluff = await self.get_fluff_by_id(fluff_id)
            fluff.hp = hp
            session.add(fluff)
            await session.commit()
            return fluff
        