from sqlalchemy import select

from app.core.config import ROLE_COLOR_MESSAGE_ID
from db import Database
from db.tables import CountingStateTable, GtnStateTable, RoleColorStateTable


class BotStateBackend(Database):
    async def get_counting_state(self, guild_id: int) -> dict:
        async with self.get_session() as session:
            stmt = select(CountingStateTable).where(CountingStateTable.guild_id == guild_id)
            result = await session.execute(stmt)
            record = result.scalars().first()
            if not record:
                record = CountingStateTable(guild_id=guild_id, status="stopped", count=0, last_author_id=None)
                session.add(record)
                await session.commit()
            return {
                "status": record.status,
                "count": record.count,
                "lastAuthor": record.last_author_id,
            }

    async def save_counting_state(self, guild_id: int, data: dict) -> None:
        async with self.get_session() as session:
            stmt = select(CountingStateTable).where(CountingStateTable.guild_id == guild_id)
            result = await session.execute(stmt)
            record = result.scalars().first()
            if not record:
                record = CountingStateTable(
                    guild_id=guild_id,
                    status=data.get("status", "stopped"),
                    count=data.get("count", 0),
                    last_author_id=data.get("lastAuthor"),
                )
                session.add(record)
            else:
                record.status = data.get("status", "stopped")
                record.count = data.get("count", 0)
                record.last_author_id = data.get("lastAuthor")
            await session.commit()

    async def get_gtn_state(self, guild_id: int) -> dict:
        async with self.get_session() as session:
            stmt = select(GtnStateTable).where(GtnStateTable.guild_id == guild_id)
            result = await session.execute(stmt)
            record = result.scalars().first()
            if not record:
                record = GtnStateTable(guild_id=guild_id, status="stopped", number=0, guesses={})
                session.add(record)
                await session.commit()
            guesses = record.guesses if isinstance(record.guesses, dict) else {}
            return {
                "status": record.status,
                "number": record.number,
                "guesses": dict(guesses),
            }

    async def save_gtn_state(self, guild_id: int, data: dict) -> None:
        async with self.get_session() as session:
            stmt = select(GtnStateTable).where(GtnStateTable.guild_id == guild_id)
            result = await session.execute(stmt)
            record = result.scalars().first()
            guesses = data.get("guesses")
            if not isinstance(guesses, dict):
                guesses = {}
            if not record:
                record = GtnStateTable(
                    guild_id=guild_id,
                    status=data.get("status", "stopped"),
                    number=data.get("number", 0),
                    guesses=dict(guesses),
                )
                session.add(record)
            else:
                record.status = data.get("status", "stopped")
                record.number = data.get("number", 0)
                record.guesses = dict(guesses)
            await session.commit()

    async def get_role_color_msg_id(self, guild_id: int) -> int | None:
        async with self.get_session() as session:
            stmt = select(RoleColorStateTable).where(RoleColorStateTable.guild_id == guild_id)
            result = await session.execute(stmt)
            record = result.scalars().first()
            if record:
                return record.message_id
            return ROLE_COLOR_MESSAGE_ID if ROLE_COLOR_MESSAGE_ID else None

    async def set_role_color_msg_id(self, guild_id: int, message_id: int) -> None:
        async with self.get_session() as session:
            stmt = select(RoleColorStateTable).where(RoleColorStateTable.guild_id == guild_id)
            result = await session.execute(stmt)
            record = result.scalars().first()
            if not record:
                record = RoleColorStateTable(guild_id=guild_id, message_id=message_id)
                session.add(record)
            else:
                record.message_id = message_id
            await session.commit()

