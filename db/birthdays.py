from datetime import date

from sqlalchemy import insert, select, delete, update

from db import Database
from db.tables import BirthdayTable


class BirthdayBackend(Database):

    async def get_all_birthdays(self, guild_id: int):
        async with self.get_session() as session:
            records = await session.execute(
                select(BirthdayTable)
                .where(BirthdayTable.guild_id == guild_id)
            )
            birthdays = records.scalars().all()
            today = date.today()

            def days_until_next_birthday(birthday_record):
                try:
                    this_year_birthday = date(today.year, birthday_record.month, birthday_record.day)

                    if this_year_birthday >= today:
                        return (this_year_birthday - today).days
                    else:
                        next_year_birthday = date(today.year + 1, birthday_record.month, birthday_record.day)
                        return (next_year_birthday - today).days
                except ValueError:
                    return 365
                except Exception as e:
                    print(e)
            return sorted(birthdays, key=days_until_next_birthday)

    async def get_users_with_birthday(self, day: int, month: int):
        async with self.get_session() as session:
            records = await session.execute(
                select(BirthdayTable).where(BirthdayTable.day == day, BirthdayTable.month == month))
            return records.scalars().all()

    async def get_user_record(self, user_id: int, guild_id: int):
        async with self.get_session() as session:
            record = await session.execute(
                select(BirthdayTable).where(BirthdayTable.user_id == user_id, BirthdayTable.guild_id == guild_id))
            return record.scalar_one_or_none()

    async def create_user_record(self, user_id: int, guild_id: int, birthday: date):
        async with self.get_session() as session:
            await session.execute(
                insert(BirthdayTable).values(user_id=user_id, guild_id=guild_id, day=birthday.day, month=birthday.month,
                                             year=birthday.year))
            await session.commit()

    async def update_user_record(self, user_id: int, guild_id: int, birthday: date):
        async with self.get_session() as session:
            await session.execute(update(BirthdayTable).where(BirthdayTable.user_id == user_id,
                                                              BirthdayTable.guild_id == guild_id).values(
                day=birthday.day, month=birthday.month, year=birthday.year))
            await session.commit()

    async def delete_user_record(self, user_id: int, guild_id: int):
        async with self.get_session() as session:
            await session.execute(
                delete(BirthdayTable).where(BirthdayTable.user_id == user_id, BirthdayTable.guild_id == guild_id))
            await session.commit()
