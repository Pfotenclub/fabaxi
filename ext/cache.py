import json
import random
from functools import lru_cache

from pathlib import Path

STATUS_FILE = Path(__file__).resolve().parent.parent / "assets" / "status.json"

# Load status messages from a JSON file and cache the result for efficiency
@lru_cache()
def load_random_status():
    with open(STATUS_FILE, encoding="utf-8") as fp:
        status = json.load(fp)
    random_status = [stuff for stuff in status["status"] if not stuff.startswith("_comment_")]
    return random_status
