from time import time

from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey

from db import Base

class BirthdayTable(Base):
    __tablename__ = "birthdays"
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer, nullable=True)

    def __init__(self, user_id, guild_id, day, month, year):
        super().__init__()
        self.user_id = user_id
        self.guild_id = guild_id
        self.day = day
        self.month = month
        self.year = year

    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])

class EconomyTable(Base):
    __tablename__ = "economy"
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    balance = Column(Integer, default=0)

    def __init__(self, user_id, guild_id, balance):
        super().__init__()
        self.user_id = user_id
        self.guild_id = guild_id
        self.balance = balance

    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])
    
class GardenBaseTable(Base):
    __tablename__ = "garden_base"
    plant_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    grow_time = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)
    gain = Column(Integer, nullable=False)
    picture_url = Column(String(255), nullable=True)

    def __init__(self, plant_id, name, description, grow_time, cost, gain, picture_url=None):
        super().__init__()
        self.plant_id = plant_id
        self.name = name
        self.description = description
        self.grow_time = grow_time # in seconds
        self.cost = cost
        self.gain = gain
        self.picture_url = picture_url

    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])

class GardenUserTable(Base):
    __tablename__ = "garden_user"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, primary_key=False, nullable=False)
    guild_id = Column(BigInteger, primary_key=False, nullable=False)
    plant_id = Column(Integer, ForeignKey("garden_base.plant_id"), nullable=False)

    def __init__(self, user_id, guild_id, plant_id):
        super().__init__()
        self.user_id = user_id
        self.guild_id = guild_id
        self.plant_id = plant_id
    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])
    
class GardenGreenhouseTable(Base):
    __tablename__ = "garden_greenhouse"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, primary_key=False, nullable=False)
    guild_id = Column(BigInteger, primary_key=False, nullable=False)
    slot1 = Column(Integer, default=-1)
    slot1_planted_time = Column(Integer, default=0)
    slot2 = Column(Integer, default=-1)
    slot2_planted_time = Column(Integer, default=0)
    slot3 = Column(Integer, default=-1)
    slot3_planted_time = Column(Integer, default=0)
    slot4 = Column(Integer, default=-1)
    slot4_planted_time = Column(Integer, default=0)
    slot5 = Column(Integer, default=-1)
    slot5_planted_time = Column(Integer, default=0)

    def __init__(self, user_id, guild_id, slot1=-1, slot1_planted_time=0, slot2=-1, slot2_planted_time=0,
                 slot3=-1, slot3_planted_time=0, slot4=-1, slot4_planted_time=0, slot5=-1, slot5_planted_time=0):
        super().__init__()
        self.user_id = user_id
        self.guild_id = guild_id
        self.slot1 = slot1
        self.slot1_planted_time = slot1_planted_time
        self.slot2 = slot2
        self.slot2_planted_time = slot2_planted_time
        self.slot3 = slot3
        self.slot3_planted_time = slot3_planted_time
        self.slot4 = slot4
        self.slot4_planted_time = slot4_planted_time
        self.slot5 = slot5
        self.slot5_planted_time = slot5_planted_time


class KarmaTable(Base):
    __tablename__ = 'karma'
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    karma = Column(Integer, default=0)
    timestamp_last_message = Column(Integer, default=0, )

    def __init__(self, user_id, guild_id, karma, timestamp_last_message=time()):
        super().__init__()
        self.user_id = user_id
        self.guild_id = guild_id
        self.karma = karma
        self.timestamp_last_message = timestamp_last_message

    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])


class RewardsTable(Base):
    __tablename__ = "rewards"
    role_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    karma_needed = Column(Integer, nullable=False)

    def __init__(self, role_id, guild_id, karma_needed):
        super().__init__()
        self.role_id = role_id
        self.guild_id = guild_id
        self.karma_needed = karma_needed

    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])


class TempVoiceTable(Base):
    __tablename__ = "temp_voice"
    owner_id = Column(BigInteger)
    channel_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger)

    def __init__(self, owner_id, channel_id, guild_id):
        super().__init__()
        self.owner_id = owner_id
        self.channel_id = channel_id
        self.guild_id = guild_id
