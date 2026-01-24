from datetime import date

from sqlalchemy import insert, select, delete, update

from db import Database
from db.tables import EconomyTable


class EconomyBackend(Database):

    async def add_balance(self, user_id: int, guild_id: int, amount: int):
        """
        Adds a new economy record for a user in a guild with the specified balance.
        
        :param user_id: User ID to add economy record for
        :param guild_id: Guild ID to add economy record for
        :param amount: Initial balance amount
        """
        async with self.get_session() as session:
            record = await session.execute(
                select(EconomyTable).where(
                    (EconomyTable.user_id == user_id) &
                    (EconomyTable.guild_id == guild_id)
                )
            )
            existing_record = record.scalar_one_or_none()
            if existing_record:
                # If record exists, update the balance instead
                stmt = update(EconomyTable).where(
                    (EconomyTable.user_id == user_id) &
                    (EconomyTable.guild_id == guild_id)
                ).values(
                    balance=EconomyTable.balance + amount
                )
                await session.execute(stmt)
                await session.commit()
                return
            else:
                stmt = insert(EconomyTable).values(
                    user_id=user_id,
                    guild_id=guild_id,
                    balance=amount
                )
                await session.execute(stmt)
                await session.commit()
    
    async def remove_balance(self, user_id: int, guild_id: int, amount: int):
        """
        Removes balance from a user's economy record in a guild.
        
        :param user_id: User ID to remove balance from
        :param guild_id: Guild ID to remove balance from
        :param amount: Amount to remove
        """
        async with self.get_session() as session:
            stmt = update(EconomyTable).where(
                (EconomyTable.user_id == user_id) &
                (EconomyTable.guild_id == guild_id)
            ).values(
                balance=EconomyTable.balance - amount
            )
            await session.execute(stmt)
            await session.commit()
################################################################################## Getters
    async def get_all_economy_records(self, guild_id: int):
        """
        Get all economy records for a guild, sorted by balance descending. (highest balance first)
        
        :param self: Bot instance
        :param guild_id: Guild ID to filter economy records
        :type guild_id: int
        """
        async with self.get_session() as session:
            records = await session.execute(
                select(EconomyTable)
                .where(EconomyTable.guild_id == guild_id)
                .order_by(EconomyTable.balance.desc())
            )
            return records.scalars().all()
        
    async def get_economy_record(self, user_id: int, guild_id: int):
        """
        Get economy record for a specific user in a guild.
        
        :param self: Bot instance
        :param user_id: User ID to get economy record for
        :type user_id: int
        :param guild_id: Guild ID to filter economy records
        :type guild_id: int
        """
        async with self.get_session() as session:
            record = await session.execute(
                select(EconomyTable)
                .where(
                    (EconomyTable.user_id == user_id) &
                    (EconomyTable.guild_id == guild_id)
                )
            )
            return record.scalar_one_or_none()