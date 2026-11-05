import logging

from sqlalchemy import insert, select, delete, update

from db import Database
from db.tables import TempVoiceTable


class TempVoiceBackend(Database):

    async def create_temp_voice(self, owner_id, channel_id, guild_id):
        async with self.get_session() as session:
            existing_record = await session.execute(
                select(TempVoiceTable).where(TempVoiceTable.channel_id == channel_id))
            if existing_record.scalars().first():
                logging.error(f"Temp voice channel already exists for channel_id={channel_id}")
                return

            insert_stmt = insert(TempVoiceTable).values(owner_id=owner_id, channel_id=channel_id, guild_id=guild_id)
            await session.execute(insert_stmt)
            await session.commit()
            logging.info(f"Created new temp voice channel for channel_id={channel_id}")

    async def delete_temp_voice(self, channel_id):
        async with self.get_session() as session:
            delete_stmt = delete(TempVoiceTable).where(TempVoiceTable.channel_id == channel_id)
            await session.execute(delete_stmt)
            await session.commit()
            logging.info(f"Deleted temp voice channel for channel_id={channel_id}")

    async def get_owner_id(self, channel_id):
        async with self.get_session() as session:
            record = await session.execute(
                select(TempVoiceTable.owner_id).where(TempVoiceTable.channel_id == channel_id))
            return record.scalars().first()

    async def get_channel_id(self, owner_id):
        async with self.get_session() as session:
            record = await session.execute(select(TempVoiceTable.channel_id).where(TempVoiceTable.owner_id == owner_id))
            return record.scalars().first()

    async def change_channel_owner_id(self, channel_id, new_owner_id):
        async with self.get_session() as session:
            update_stmt = update(TempVoiceTable).where(TempVoiceTable.channel_id == channel_id).values(
                owner_id=new_owner_id)
            await session.execute(update_stmt)
            await session.commit()
            logging.info(f"Changed owner_id for channel_id={channel_id} to new_owner_id={new_owner_id}")
