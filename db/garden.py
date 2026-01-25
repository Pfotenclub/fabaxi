from datetime import datetime
import discord

from sqlalchemy import insert, select, delete, update

from db import Database
from db.tables import GardenBaseTable, GardenUserTable, GardenGreenhouseTable
from db.economy import EconomyBackend

from ext.system import send_system_message


class GardenBackend(Database):

    async def add_plant(self, user_id: int, guild_id: int, plant_id: int):
        """
        Docstring for add_plant
        
        :param user_id: User ID from User to add plant for
        :param guild_id: Guild ID from Guild to add plant for
        :param plant_id: Plant ID from GardenBaseTable to add
        """
        async with self.get_session() as session:
            stmt = insert(GardenUserTable).values(
                user_id=user_id,
                guild_id=guild_id,
                plant_id=plant_id,
            )
        await session.execute(stmt)
        await session.commit()

    async def create_greenhouse(self, user_id: int, guild_id: int):
        """
        Docstring for create_greenhouse
        
        :param user_id: User ID from User to create greenhouse for
        :param guild_id: Guild ID from Guild to create greenhouse for
        """
        async with self.get_session() as session:
            stmt = insert(GardenGreenhouseTable).values(
                user_id=user_id,
                guild_id=guild_id,
                slot1=0,
            )
        await session.execute(stmt)
        await session.commit()
    
    async def upgrade_greenhouse(self, user_id: int, guild_id: int, slot: str):
        """
        Upgrades the user's greenhouse by unlocking a new slot.
        Does not check if the slot is already unlocked and will not remove balance for the upgrade.
        
        :param user_id: User ID from User to upgrade greenhouse for
        :param guild_id: Guild ID from Guild to upgrade greenhouse for
        :param slot: Slot column name in greenhouse to unlock, possible values: slot2, slot3, slot4, slot5
        """
        slot_column = f"{slot}"
        
        async with self.get_session() as session:
            stmt = update(GardenGreenhouseTable).where(
                (GardenGreenhouseTable.user_id == user_id) &
                (GardenGreenhouseTable.guild_id == guild_id)
            ).values(
                **{slot_column: 0}
            )
        await session.execute(stmt)
        await session.commit()
    
    async def plant_seed_in_greenhouse(self, user_id: int, guild_id: int, plant_id: int, slot: str):
        """
        Plants a seed in a specific slot in the user's greenhouse.
        Does not check if the slot is already occupied and will not remove balance for the plant.
        
        :param user_id: User ID from User to plant seed for
        :param guild_id: Guild ID from Guild to plant seed for
        :param plant_id: Plant ID from GardenBaseTable to plant
        :param slot: Slot column name in greenhouse to plant seed in, possible values: slot1, slot2, slot3, slot4, slot5
        """
        now = int(datetime.now().timestamp())
        slot_column = f"{slot}"
        slot_planted_time_column = f"{slot}_planted_time"
        
        async with self.get_session() as session:
            stmt = update(GardenGreenhouseTable).where(
                (GardenGreenhouseTable.user_id == user_id) &
                (GardenGreenhouseTable.guild_id == guild_id)
            ).values(
                **{slot_column: plant_id,
                   slot_planted_time_column: now}
            )
        await session.execute(stmt)
        await session.commit()

    async def buy_plant(self, user_id: int, guild_id: int, plant_id: int):
        """
        Docstring for buy_plant
        
        :param self: Description
        :param user_id: Description
        :type user_id: int
        :param guild_id: Description
        :type guild_id: int
        :param plant_id: Description
        :type plant_id: int
        """
        plant = await self.get_plant_name(plant_id=plant_id)
        await EconomyBackend().remove_balance(user_id=user_id, guild_id=guild_id, amount=await self.get_plant_cost(plant_id=plant_id))
        await self.add_plant(user_id=user_id, guild_id=guild_id, plant_id=plant_id)
    
    async def remove_plant_from_user(self, user_id: int, guild_id: int, plant_id: int):
        """
        Docstring for remove_plant_from_user
        
        :param user_id: User ID from User to remove plant for
        :param guild_id: Guild ID from Guild to remove plant for
        :param plant_id: Plant ID from GardenBaseTable to remove
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GardenUserTable)
                .where(
                    (GardenUserTable.user_id == user_id) &
                    (GardenUserTable.guild_id == guild_id) &
                    (GardenUserTable.plant_id == plant_id)
                )
            )
            plant_entry = result.scalars().first()

        async with self.get_session() as session:
            stmt = delete(GardenUserTable).where(
                (GardenUserTable.user_id == user_id) &
                (GardenUserTable.guild_id == guild_id) &
                (GardenUserTable.plant_id == plant_id) & 
                (GardenUserTable.id == plant_entry.id)
            )
        await session.execute(stmt)
        await session.commit()
    
    async def harvest_plant_from_greenhouse(self, user_id: int, guild_id: int, slot: str):
        """
        Harvests a plant from a specific slot in the user's greenhouse.
        Also gives the money for the harvested plant.
        Does not check if the plant is fully grown.
        
        :param user_id: User ID from User to harvest plant for
        :param guild_id: Guild ID from Guild to harvest plant for
        :param slot: Slot column name in greenhouse to harvest plant from, possible values: slot1, slot2, slot3, slot4, slot5
        """
        slot_column = f"{slot}"
        slot_planted_time_column = f"{slot}_planted_time"
        
        async with self.get_session() as session:
            result = await session.execute(
                select(getattr(GardenGreenhouseTable, slot_column)).where(
                    (GardenGreenhouseTable.user_id == user_id) &
                    (GardenGreenhouseTable.guild_id == guild_id)
                )
            )
            plant_id = result.scalar_one_or_none()
            plant_gain = await self.get_plant_gain(plant_id=plant_id)
            await EconomyBackend().add_balance(user_id=user_id, guild_id=guild_id, amount=plant_gain)
            stmt = update(GardenGreenhouseTable).where(
                (GardenGreenhouseTable.user_id == user_id) &
                (GardenGreenhouseTable.guild_id == guild_id)
            ).values(
                **{slot_column: 0,
                   slot_planted_time_column: 0}
            )
        await session.execute(stmt)
        await session.commit()
    
################################################################################## Getters    
    async def get_all_plants(self):
        """
        Gets all plants from GardenBaseTable.
        This returns a list with all plant entries.
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GardenBaseTable)
            )
            plants = result.scalars().all()
            return plants
    
    async def get_grown_time(self, plant_id: int):
        """
        Gets the time required for a plant to grow from GardenBaseTable.
        
        :param plant_id: Plant ID from GardenBaseTable to get grown time for
        :type plant_id: int
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GardenBaseTable.grow_time).where(GardenBaseTable.plant_id == plant_id)
            )
            grown_time = result.scalar_one_or_none()
            return grown_time

    async def get_plant_cost(self, plant_id: int):
        """
        Gets the cost of a plant from GardenBaseTable.
        
        :param plant_id: Plant ID from GardenBaseTable to get cost for
        :type plant_id: int
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GardenBaseTable.cost).where(GardenBaseTable.plant_id == plant_id)
            )
            cost = result.scalar_one_or_none()
            return cost
    async def get_plant_gain(self, plant_id: int):
        """
        Gets the gain of a plant from GardenBaseTable.
        
        :param plant_id: Plant ID from GardenBaseTable to get gain for
        :type plant_id: int
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GardenBaseTable.gain).where(GardenBaseTable.plant_id == plant_id)
            )
            gain = result.scalar_one_or_none()
            return gain
################################################ User Getters
    async def get_all_plants_from_user(self, user_id: int, guild_id: int):
        """
        Gets all plants from GardenUserTable for a specific user in a guild.
        This returns a list with all plant entries for the user.
        If you want a summary, choose get_plant_summary_from_user instead.
        
        :param user_id: User ID from User to get plants for
        :param guild_id: Guild ID from Guild to get plants for
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GardenUserTable).where(
                    (GardenUserTable.user_id == user_id) &
                    (GardenUserTable.guild_id == guild_id)
                )
            )
            plants = result.scalars().all()
            return plants
        
    async def get_plant_summary_from_user(self, user_id: int, guild_id: int):
        """
        Gets a summary of plants from GardenUserTable for a specific user in a guild.
        This returns a dictionary (sorted descending) with plant IDs as keys and their quantities as values.
        
        :param user_id: User ID from User to get plant summary for
        :param guild_id: Guild ID from Guild to get plant summary for
        """
        plants = await self.get_all_plants_from_user(user_id=user_id, guild_id=guild_id)
        plants_sum = {}
        for p in plants:
            if p.plant_id in plants_sum:
                plants_sum[p.plant_id] += 1
            else:
                plants_sum[p.plant_id] = 1
        plants_sum = dict(sorted(plants_sum.items(), key=lambda item: item[1], reverse=True))
        return plants_sum
    
    async def get_greenhouse_from_user(self, user_id: int, guild_id: int):
        """
        Gets all greenhouse slots from GardenGreenhouseTable for a specific user in a guild.
        
        :param user_id: User ID from User to get greenhouse for
        :param guild_id: Guild ID from Guild to get greenhouse for
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GardenGreenhouseTable).where(
                    (GardenGreenhouseTable.user_id == user_id) &
                    (GardenGreenhouseTable.guild_id == guild_id) &
                    (
                        (GardenGreenhouseTable.slot1 != -1) |
                        (GardenGreenhouseTable.slot2 != -1) |
                        (GardenGreenhouseTable.slot3 != -1) |
                        (GardenGreenhouseTable.slot4 != -1) |
                        (GardenGreenhouseTable.slot5 != -1)
                    )
                )
            )
            greenhouse = result.scalars().all()
            return greenhouse
    
    
################################################################################## Helpers
    async def get_plant_name(self, plant_id: int):
        """
        Gets the name of a plant from GardenBaseTable by its ID.
        
        :param plant_id: Plant ID from GardenBaseTable to get name for
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GardenBaseTable.name).where(GardenBaseTable.plant_id == plant_id)
            )
            plant = result.scalar_one_or_none()
            return plant

    async def get_plant_description(self, plant_id: int):
        """
        Gets the description of a plant from GardenBaseTable by its ID.
        
        :param plant_id: Plant ID from GardenBaseTable to get description for
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GardenBaseTable.description).where(GardenBaseTable.plant_id == plant_id)
            )
            plant = result.scalar_one_or_none()
            return plant
        
    async def get_plant_grown_time(self, user_id: int, guild_id: int, plant_id: int, slot: str):
        """
        Gets the remaining grown time for a plant in a specific slot in the user's greenhouse.
        Value will be returned in minutes
        
        :param user_id: User ID from User to get plant grown time for
        :type user_id: int
        :param guild_id: Guild ID from Guild to get plant grown time for
        :type guild_id: int
        :param plant_id: Plant ID from GardenBaseTable to get plant grown time for
        :type plant_id: int
        :param slot: Slot column name in greenhouse to get plant grown time for, possible values: slot1, slot2, slot3, slot4, slot5
        :type slot: str
        """
        slot_planted_time_column = f"{slot}_planted_time"
        
        async with self.get_session() as session:
            result = await session.execute(
                select(getattr(GardenGreenhouseTable, slot_planted_time_column)).where(
                    (GardenGreenhouseTable.user_id == user_id) &
                    (GardenGreenhouseTable.guild_id == guild_id)
                )
            )
            planted_time = result.scalar_one_or_none()
            grow_time = await self.get_grown_time(plant_id=plant_id)
            planted_time = int(((planted_time + grow_time) - datetime.now().timestamp()) / 60) # Convert to minutes
            return planted_time