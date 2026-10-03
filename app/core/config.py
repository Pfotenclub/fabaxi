import os
import tomllib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = Path("/bot/config.toml") if Path("/bot/config.toml").exists() else PROJECT_ROOT / "config.toml"

def load_config():
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)

cfg = load_config()

# Tokens & Guilds
TOKEN = os.getenv("TOKEN")
ENVIRONMENT = cfg["general"]["environment"].upper()
CURRENT_GUILD_ID = cfg["general"]["server_id"]

# Owner / Bot Master IDs ("Cult Leaders")
OWNER_IDS = cfg["general"]["owner_ids"]

# Persistent State Data Directory
if ENVIRONMENT == "PROD":
    DATA_DIR = Path("/db")
else:
    DATA_DIR = PROJECT_ROOT / "data"

# Static Assets
ASSETS_DIR = PROJECT_ROOT / "assets"
RULES_IMAGE_PATH = ASSETS_DIR / "images" / "rules.png"
STATUS_FILE_PATH = ASSETS_DIR / "status.json"

# Join to Create Temporary Voice Channels
JOIN_TO_CREATE_VOICE = cfg["voice"]["join_to_create_voice"]
JOIN_TO_CREATE_PARENT = cfg["voice"]["join_to_create_parent"]
JOIN_TO_CREATE_PREFIX = cfg["voice"]["join_to_create_prefix"]
JOIN_TO_CREATE_CHANNEL_NAME = cfg["voice"]["join_to_create_channel_name"]

# Welcome Roles (assigned on member join)
WELCOME_ROLE_IDS = cfg["roles"]["welcome"]

# Birthday System Configuration
BIRTHDAY_GUILD_ID = CURRENT_GUILD_ID
BIRTHDAY_ANNOUNCEMENT_CHANNEL_ID = cfg["general"]["announcement_channel_id"]
BIRTHDAY_ROLE_ID = cfg["roles"]["birthday"]

# Karma Tracking Ignored Channels (e.g. bots, spam, games)
IGNORED_KARMA_CHANNELS = cfg["karma"]["ignored_karma_channels"]

# Nightclub Verification Role & Staff
NIGHTCLUB_ROLE_ID = cfg["roles"]["nightclub"]
UNDERAGE_ROLE_ID = cfg["roles"]["underage"]
STAFF_ROLE_ID = cfg["roles"]["burgeramt"]
BURGERAMT_CHANNEL_ID = cfg["general"]["burgeramt_channel_id"]

# Minigames Channels
COUNTING_CHANNEL_ID = cfg["minigames"]["counting_channel_id"]
GTN_CHANNEL_ID = cfg["minigames"]["gtn_channel_id"]

# Admin / Moderation Channels
BAN_REPORT_CHANNEL_ID = cfg["general"]["admin_channel_id"]

# System stuff
API_PORT = cfg["system"]["api_port"]
WEBHOOK_URL = cfg["system"]["webhook_url"]
MEDIA_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.mp4', '.mov', '.webm')