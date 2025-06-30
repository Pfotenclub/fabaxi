from time import time

from sqlalchemy import Column, Integer, BigInteger, String

from db import Base


class ReactionRoleTable(Base):
    __tablename__ = 'reaction_role'
    role_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    role_color_hex = Column(String(50), nullable=True)
    role_emote_id = Column(BigInteger, nullable=True)

    def __init__(self, role_id, guild_id, role_name, role_color, role_emote):
        super().__init__()
        self.role_id = role_id
        self.guild_id = guild_id
        self.role_name = role_name
        self.role_color = role_color
        self.role_emote = role_emote

    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])


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
