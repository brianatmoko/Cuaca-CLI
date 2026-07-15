import hashlib
import json
import os
import time

CACHE_DIR = os.path.expanduser("~/.cache/weather-cli")
DEFAULT_TTL = 300


def _path(key: str) -> str:
    h = hashlib.md5(key.encode()).hexdigest()
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{h}.json")


def cache_get(key: str, ttl: int = DEFAULT_TTL):
    path = _path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        if time.time() - data["ts"] > ttl:
            return None
        return data["value"]
    except (json.JSONDecodeError, OSError):
        return None


def cache_set(key: str, value, ttl: int = DEFAULT_TTL) -> None:
    path = _path(key)
    with open(path, "w") as f:
        json.dump({"ts": time.time(), "value": value}, f)
