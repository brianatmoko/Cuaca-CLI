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
        age = time.time() - data["ts"]
        if age > ttl:
            return None
        return data["value"]
    except (json.JSONDecodeError, OSError):
        return None


def cache_set(key: str, value, ttl: int = DEFAULT_TTL) -> None:
    path = _path(key)
    with open(path, "w") as f:
        json.dump({"ts": time.time(), "value": value}, f)


def cache_cleanup(max_age: int = 86400) -> int:
    """Remove cache files older than max_age seconds. Returns count removed."""
    if not os.path.isdir(CACHE_DIR):
        return 0
    now = time.time()
    removed = 0
    for fname in os.listdir(CACHE_DIR):
        fpath = os.path.join(CACHE_DIR, fname)
        if not fname.endswith(".json"):
            continue
        try:
            age = now - os.path.getmtime(fpath)
            if age > max_age:
                os.remove(fpath)
                removed += 1
        except OSError:
            pass
    return removed


def cache_stats() -> dict:
    """Return cache statistics."""
    if not os.path.isdir(CACHE_DIR):
        return {"files": 0, "size_kb": 0}
    total_size = 0
    count = 0
    for fname in os.listdir(CACHE_DIR):
        fpath = os.path.join(CACHE_DIR, fname)
        if fname.endswith(".json") and os.path.isfile(fpath):
            count += 1
            total_size += os.path.getsize(fpath)
    return {"files": count, "size_kb": round(total_size / 1024, 1)}
