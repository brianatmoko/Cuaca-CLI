import json
import os

CONFIG_DIR = os.path.expanduser("~/.config/weather-cli")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
FAVORITES_PATH = os.path.join(CONFIG_DIR, "favorites.json")

DEFAULTS = {
    "default_city": "Jakarta",
    "forecast_days": 3,
    "color": True,
    "cache_ttl": 300,
    "units": "metric",
}


def load() -> dict:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        cfg = dict(DEFAULTS)
        save(cfg)
        return cfg
    try:
        with open(CONFIG_PATH) as f:
            return {**DEFAULTS, **json.load(f)}
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)


def save(cfg: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def load_favorites() -> list[str]:
    if not os.path.exists(FAVORITES_PATH):
        return []
    with open(FAVORITES_PATH) as f:
        return json.load(f)


def save_favorites(favs: list[str]) -> None:
    with open(FAVORITES_PATH, "w") as f:
        json.dump(favs, f, indent=2)
