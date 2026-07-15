import json
import urllib.request
from .models import City

IPAPI = "http://ip-api.com/json/?fields=city,lat,lon,countryCode"


def detect_city() -> City | None:
    try:
        req = urllib.request.Request(IPAPI, headers={"User-Agent": "weather-cli/2.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        if data.get("countryCode") == "ID" and data.get("city"):
            return City(
                name=data["city"],
                lat=data["lat"],
                lon=data["lon"],
                province="",
                country="Indonesia",
            )
    except Exception:
        pass
    return None
