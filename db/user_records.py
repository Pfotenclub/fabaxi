from datetime import date

from sqlalchemy import insert, select, update

from db import Database
from db.tables import BirthdayTable


class UserRecords(Database):

    async def get_user_record(self, user_id, guild_id):
        async with self.get_session() as session:
            record = await session.execute(
                select(BirthdayTable).where(BirthdayTable.user_id == user_id, BirthdayTable.guild_id == guild_id))
            return record.scalars().first()

    async def get_users_with_birthday(self, day, month):
        async with self.get_session() as session:
            records = await session.execute(
                select(BirthdayTable).where(BirthdayTable.day == day, BirthdayTable.month == month))
            return records.scalars().all()

    async def create_user_record(self, user_id, guild_id, birthday: date):
        async with self.get_session() as session:
            await session.execute(
                insert(BirthdayTable).values(user_id=user_id, guild_id=guild_id, day=birthday.day, month=birthday.month,
                                             year=birthday.year))
            await session.commit()

    async def edit_user_record(self, user_id, guild_id, birthday: date):
        async with self.get_session() as session:
            await session.execute(update(BirthdayTable).where(BirthdayTable.user_id == user_id,
                                                              BirthdayTable.guild_id == guild_id).values(
                day=birthday.day, month=birthday.month, year=birthday.year))
            await session.commit()
