import logging

from sqlalchemy import insert, select, delete, update

from db import Database
from db.tables import EconomyTable


class EconomyBackend(Database):

    async def get_balance(self, user_id, guild_id):
        async with self.get_session() as session:
            record = await session.execute(
                select(EconomyTable.balance).where(EconomyTable.user_id == user_id).where(EconomyTable.guild_id == guild_id))
            return record.scalars().first()
    
    async def set_balance(self, user_id, guild_id, balance):
        async with self.get_session() as session:
            record = await session.execute(
                select(EconomyTable.balance).where(EconomyTable.user_id == user_id).where(EconomyTable.guild_id == guild_id))
            if record.scalars().first():
                await session.execute(
                    update(EconomyTable).where(EconomyTable.user_id == user_id).where(EconomyTable.guild_id == guild_id).values(balance=balance))
            else:
                await session.execute(
                    insert(EconomyTable).values(user_id=user_id, guild_id=guild_id, balance=balance))
            await session.commit()