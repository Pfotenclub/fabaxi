import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Runtime Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "DEV")

# Tokens & Guilds
DEV_TOKEN = os.getenv("DEV_TOKEN")
PROD_TOKEN = os.getenv("PROD_TOKEN")
TOKEN = PROD_TOKEN if ENVIRONMENT == "PROD" else DEV_TOKEN

DEV_SERVER = int(os.getenv("DEV_SERVER", 0)) if os.getenv("DEV_SERVER") else None
PROD_SERVER = int(os.getenv("PROD_SERVER", 0)) if os.getenv("PROD_SERVER") else None
CURRENT_GUILD_ID = PROD_SERVER if ENVIRONMENT == "PROD" else DEV_SERVER

# Owner / Bot Master IDs ("Cult Leaders")
OWNER_IDS = [327880195476422656, 474947907913515019]

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
JOIN_TO_CREATE_VOICE = int(os.getenv("JOINTOCREATEVOICE", 0))
JOIN_TO_CREATE_PARENT = int(os.getenv("JOINTOCREATEPARENT", 0))

# Welcome Roles (assigned on member join)
WELCOME_ROLE_IDS = [
    1230984456186237008,  # Interests role
    1229073628658794688,  # About Me role
    1341774758076874832,  # Custom Roles role
]

# Birthday System Configuration
BIRTHDAY_GUILD_ID = 1056514064081231872
BIRTHDAY_ANNOUNCEMENT_CHANNEL_ID = 1191397658514956308
BIRTHDAY_ROLE_ID = 1342827586648150076

# Karma Tracking Ignored Channels (e.g. bots, spam, games)
IGNORED_KARMA_CHANNELS = [
    1229062537954332782,  # commands channel
    1337733289695514725,  # counting channel
    1339010562964586647,  # cult leader channel
    1462546344064586031,  # guess the number channel (prod)
    1462546129106501837,  # guess the number channel (dev)
    1283842433284837396,  # burgeramt channel
]

# Nightclub Verification Role & Staff
NIGHTCLUB_ROLE_ID = 1310647737712119879
UNDERAGE_ROLE_ID = 1229064333993050123
STAFF_ROLE_ID = 1311047394074300498
BURGERAMT_CHANNEL_ID = 1283842433284837396

# Minigames Channels
COUNTING_CHANNEL_ID = 1337733289695514725 if ENVIRONMENT == "PROD" else 1335743804346470411
GTN_CHANNEL_ID = 1462546344064586031 if ENVIRONMENT == "PROD" else 1462546129106501837

# Admin / Moderation Channels
BAN_REPORT_CHANNEL_ID = 1345384433863360542
