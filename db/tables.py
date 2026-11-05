from time import time

from sqlalchemy import Column, Integer, BigInteger, String, JSON

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


class CountingStateTable(Base):
    __tablename__ = "counting_state"
    guild_id = Column(BigInteger, primary_key=True)
    status = Column(String(32), nullable=False, default="stopped")
    count = Column(Integer, nullable=False, default=0)
    last_author_id = Column(BigInteger, nullable=True)

    def __init__(self, guild_id, status="stopped", count=0, last_author_id=None):
        super().__init__()
        self.guild_id = guild_id
        self.status = status
        self.count = count
        self.last_author_id = last_author_id


class GtnStateTable(Base):
    __tablename__ = "gtn_state"
    guild_id = Column(BigInteger, primary_key=True)
    status = Column(String(32), nullable=False, default="stopped")
    number = Column(Integer, nullable=False, default=0)
    guesses = Column(JSON, nullable=False)

    def __init__(self, guild_id, status="stopped", number=0, guesses=None):
        super().__init__()
        self.guild_id = guild_id
        self.status = status
        self.number = number
        self.guesses = guesses if guesses is not None else {}


class RoleColorStateTable(Base):
    __tablename__ = "role_color_state"
    guild_id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger, nullable=False)

    def __init__(self, guild_id, message_id):
        super().__init__()
        self.guild_id = guild_id
        self.message_id = message_id
