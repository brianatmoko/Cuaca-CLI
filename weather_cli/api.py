import json
import urllib.request
import urllib.error
import time
from .models import City, CurrentWeather, DailyForecast, HourlyData, AQIData
from .cache import cache_get, cache_set
from .errors import NetworkError, APIError

WEATHER_API = "https://api.open-meteo.com/v1/forecast"
GEO_API = "https://geocoding-api.open-meteo.com/v1/search"
AQI_API = "https://air-quality-api.open-meteo.com/v1/air-quality"

CURRENT_PARAMS = (
    "temperature_2m,relative_humidity_2m,apparent_temperature,"
    "precipitation,weather_code,wind_speed_10m,wind_direction_10m"
)
DAILY_PARAMS = (
    "temperature_2m_max,temperature_2m_min,weather_code,"
    "precipitation_sum,sunrise,sunset,uv_index_max,wind_speed_10m_max"
)
HOURLY_PARAMS = (
    "temperature_2m,precipitation_probability,weather_code,wind_speed_10m"
)
AQI_PARAMS = "european_aqi,us_aqi,pm2_5,pm10,ozone,nitrogen_dioxide"

MAX_RETRIES = 2
RETRY_DELAY = 1
TIMEOUT = 15


def _fetch_json(url: str, retries: int = MAX_RETRIES) -> dict:
    last_error = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "weather-cli/2.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(RETRY_DELAY * (attempt + 1))
                last_error = APIError("Rate limit exceeded")
                continue
            raise APIError(f"HTTP {e.code}: {e.reason}") from e
        except urllib.error.URLError as e:
            last_error = NetworkError(str(e.reason))
            if attempt < retries:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise last_error
        except (json.JSONDecodeError, OSError) as e:
            raise APIError(str(e)) from e
    raise last_error or APIError("Request failed")


def fetch_weather(city: City, days: int = 3, hourly: bool = False) -> dict:
    cache_key = f"weather:{city.lat}:{city.lon}:{days}:{hourly}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    url = (
        f"{WEATHER_API}?latitude={city.lat}&longitude={city.lon}"
        f"&current={CURRENT_PARAMS}"
        f"&daily={DAILY_PARAMS}"
        f"&timezone=auto&forecast_days={days}"
    )
    if hourly:
        url += f"&hourly={HOURLY_PARAMS}"

    data = _fetch_json(url)
    cache_set(cache_key, data)
    return data


def fetch_aqi(city: City) -> dict:
    cache_key = f"aqi:{city.lat}:{city.lon}"
    cached = cache_get(cache_key, ttl=3600)
    if cached:
        return cached

    url = (
        f"{AQI_API}?latitude={city.lat}&longitude={city.lon}"
        f"&current={AQI_PARAMS}"
    )
    try:
        data = _fetch_json(url)
    except APIError:
        return {}
    cache_set(cache_key, data, ttl=3600)
    return data


def parse_current(raw: dict) -> CurrentWeather:
    c = raw["current"]
    return CurrentWeather(
        temp=c["temperature_2m"],
        feels_like=c["apparent_temperature"],
        humidity=c["relative_humidity_2m"],
        precip=c["precipitation"],
        wind_speed=c["wind_speed_10m"],
        wind_dir=c["wind_direction_10m"],
        weather_code=c["weather_code"],
        time=c["time"],
    )


def parse_daily(raw: dict) -> list[DailyForecast]:
    d = raw["daily"]
    return [
        DailyForecast(
            date=d["time"][i],
            temp_max=d["temperature_2m_max"][i],
            temp_min=d["temperature_2m_min"][i],
            weather_code=d["weather_code"][i],
            precip_sum=d["precipitation_sum"][i],
            sunrise=d["sunrise"][i],
            sunset=d["sunset"][i],
            uv_max=d["uv_index_max"][i],
            wind_speed=d["wind_speed_10m_max"][i],
        )
        for i in range(len(d["time"]))
    ]


def parse_hourly(raw: dict) -> list[HourlyData]:
    h = raw["hourly"]
    return [
        HourlyData(
            time=h["time"][i],
            temp=h["temperature_2m"][i],
            precip_prob=h["precipitation_probability"][i],
            weather_code=h["weather_code"][i],
            wind_speed=h["wind_speed_10m"][i],
        )
        for i in range(len(h["time"]))
    ]


def parse_aqi(raw: dict) -> AQIData:
    if not raw or "current" not in raw:
        return AQIData()
    c = raw["current"]
    return AQIData(
        european_aqi=c.get("european_aqi"),
        us_aqi=c.get("us_aqi"),
        pm25=c.get("pm2_5"),
        pm10=c.get("pm10"),
        ozone=c.get("ozone"),
        no2=c.get("nitrogen_dioxide"),
    )
