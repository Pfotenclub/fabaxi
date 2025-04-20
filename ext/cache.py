import json
import random
from functools import lru_cache


@lru_cache()
async def load_random_status():
    with open("etc/status.json", encoding="utf-8") as fp:
        status = json.load(fp)
    random_status = [stuff for stuff in status["status"] if not stuff.startswith("_comment_")]
    return random_status
