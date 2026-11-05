import json
import os
import tomllib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_explicit_cfg = os.getenv("CONFIG_PATH")
if _explicit_cfg and Path(_explicit_cfg).exists():
    CONFIG_FILE = Path(_explicit_cfg)
elif Path("/bot/config/config.toml").exists():
    CONFIG_FILE = Path("/bot/config/config.toml")
elif Path("/bot/config.toml").exists():
    CONFIG_FILE = Path("/bot/config.toml")
elif (PROJECT_ROOT / "config.toml").exists():
    CONFIG_FILE = PROJECT_ROOT / "config.toml"
elif (PROJECT_ROOT / "config.example.toml").exists():
    CONFIG_FILE = PROJECT_ROOT / "config.example.toml"
else:
    CONFIG_FILE = None


def load_config() -> dict:
    if CONFIG_FILE and CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            return tomllib.load(f)
    return {}


def _env_int(name: str, default: int = 0) -> int:
    val = os.getenv(name)
    return int(val) if val is not None and val.strip() != "" else int(default)


def _env_int_list(name: str, default: list[int] | None = None) -> list[int]:
    val = os.getenv(name)
    if val is not None and val.strip() != "":
        raw = val.strip()
        if raw.startswith("["):
            return [int(x) for x in json.loads(raw)]
        return [int(x.strip()) for x in raw.split(",") if x.strip()]
    return list(default) if default is not None else []


cfg = load_config()
_general = cfg.get("general", {})
_credentials = cfg.get("credentials", {})
_db_cfg = cfg.get("database", {})
_roles = cfg.get("roles", {})
_voice = cfg.get("voice", {})
_minigames = cfg.get("minigames", {})
_karma = cfg.get("karma", {})
_system = cfg.get("system", {})

# General Settings
ENVIRONMENT = (os.getenv("ENVIRONMENT") or _general.get("environment", "PROD")).upper()
CURRENT_GUILD_ID = _env_int("SERVER_ID", _general.get("server_id", 0))
OWNER_IDS = _env_int_list("OWNER_IDS", _general.get("owner_ids", []))
LOG_LEVEL = (os.getenv("LOG_LEVEL") or _system.get("log_level", "INFO")).upper()

# Credentials & Secrets (Environment variables override config.toml)
TOKEN = os.getenv("TOKEN") or _credentials.get("token") or ""
API_SECRET = os.getenv("API_SECRET") or _credentials.get("api_secret") or ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or _credentials.get("openai_api_key") or ""
UPTIME_KUMA_PUSH_URL = os.getenv("UPTIME_KUMA_PUSH_URL") or _system.get("uptime_kuma_push_url") or ""
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or _system.get("webhook_url") or ""

# Database Configuration (Environment variables override config.toml)
DB_HOST = os.getenv("DB_HOST") or _db_cfg.get("host", "127.0.0.1")
DB_PORT = _env_int("DB_PORT", _db_cfg.get("port", 3306))
DB_NAME = os.getenv("DB_NAME") or _db_cfg.get("name", "fabaxi")
DB_USER = os.getenv("DB_USER") or _db_cfg.get("user", "fabaxi")
DB_PW = os.getenv("DB_PW") or _db_cfg.get("password", "")

# Role Colors (Mapping: "role_id" -> "emoji") & Default Message / Channel ID
ROLE_COLORS = cfg.get("role_colors", {})
ROLE_COLOR_MESSAGE_ID = _env_int("ROLE_COLOR_MESSAGE_ID", _roles.get("role_color_message_id", 0))
ROLE_COLORS_CHANNEL_ID = _env_int("ROLE_COLORS_CHANNEL_ID", _general.get("role_colors_channel_id", 0))

# Static Read-Only Assets (baked into container image)
ASSETS_DIR = PROJECT_ROOT / "assets"
RULES_IMAGE_PATH = ASSETS_DIR / "images" / "rules.png"
STATUS_FILE_PATH = ASSETS_DIR / "status.json"

# Join to Create Temporary Voice Channels
JOIN_TO_CREATE_VOICE = _env_int("JOIN_TO_CREATE_VOICE", _voice.get("join_to_create_voice", 0))
JOIN_TO_CREATE_PARENT = _env_int("JOIN_TO_CREATE_PARENT", _voice.get("join_to_create_parent", 0))
JOIN_TO_CREATE_PREFIX = os.getenv("JOIN_TO_CREATE_PREFIX") or _voice.get("join_to_create_prefix", "🔊・")
JOIN_TO_CREATE_CHANNEL_NAME = (
    os.getenv("JOIN_TO_CREATE_CHANNEL_NAME") or _voice.get("join_to_create_channel_name", "{username}'s Channel")
)

# Welcome Roles (assigned on member join)
WELCOME_ROLE_IDS = _env_int_list("WELCOME_ROLE_IDS", _roles.get("welcome", []))

# Birthday System Configuration
BIRTHDAY_GUILD_ID = CURRENT_GUILD_ID
BIRTHDAY_ANNOUNCEMENT_CHANNEL_ID = _env_int(
    "ANNOUNCEMENT_CHANNEL_ID", _general.get("announcement_channel_id", 0)
)
BIRTHDAY_ROLE_ID = _env_int("BIRTHDAY_ROLE_ID", _roles.get("birthday", 0))

# Karma Tracking Ignored Channels & Reaction Emojis
IGNORED_KARMA_CHANNELS = _env_int_list("IGNORED_KARMA_CHANNELS", _karma.get("ignored_karma_channels", []))
UPVOTE_EMOJI_ID = _env_int("UPVOTE_EMOJI_ID", _karma.get("upvote_emoji_id", 0))
DOWNVOTE_EMOJI_ID = _env_int("DOWNVOTE_EMOJI_ID", _karma.get("downvote_emoji_id", 0))

# Nightclub Verification Role, Channel & Staff
NIGHTCLUB_ROLE_ID = _env_int("NIGHTCLUB_ROLE_ID", _roles.get("nightclub", 0))
NIGHTCLUB_APPROVAL_CHANNEL_ID = _env_int(
    "NIGHTCLUB_APPROVAL_CHANNEL_ID", _general.get("nightclub_approval_channel_id", 0)
)
UNDERAGE_ROLE_ID = _env_int("UNDERAGE_ROLE_ID", _roles.get("underage", 0))
STAFF_ROLE_ID = _env_int("STAFF_ROLE_ID", _roles.get("burgeramt", 0))
BURGERAMT_CHANNEL_ID = _env_int("BURGERAMT_CHANNEL_ID", _general.get("burgeramt_channel_id", 0))

# Minigames Channels
COUNTING_CHANNEL_ID = _env_int("COUNTING_CHANNEL_ID", _minigames.get("counting_channel_id", 0))
GTN_CHANNEL_ID = _env_int("GTN_CHANNEL_ID", _minigames.get("gtn_channel_id", 0))

# Admin / Moderation Channels
BAN_REPORT_CHANNEL_ID = _env_int("ADMIN_CHANNEL_ID", _general.get("admin_channel_id", 0))

# System / Internal REST API
API_PORT = _env_int("API_PORT", _system.get("api_port", 62299))
