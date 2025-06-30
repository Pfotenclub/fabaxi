from datetime import date

from sqlalchemy import insert, select, delete, update

from db import Database
from db.tables import BirthdayTable


class ReactionRoleBackend(Database):


    async def create_reaction_role(self, guild_id:int, role_id, emote_id, color_hex):
        pass