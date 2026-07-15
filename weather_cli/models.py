from dataclasses import dataclass, field
from typing import Optional


@dataclass
class City:
    name: str
    lat: float
    lon: float
    province: str = ""
    country: str = "Indonesia"

    @property
    def label(self) -> str:
        return f"{self.name}, {self.province}" if self.province else self.name


@dataclass
class CurrentWeather:
    temp: float
    feels_like: float
    humidity: int
    precip: float
    wind_speed: float
    wind_dir: int
    weather_code: int
    time: str


@dataclass
class DailyForecast:
    date: str
    temp_max: float
    temp_min: float
    weather_code: int
    precip_sum: float
    sunrise: str
    sunset: str
    uv_max: float
    wind_speed: float


@dataclass
class HourlyData:
    time: str
    temp: float
    precip_prob: int
    weather_code: int
    wind_speed: float


@dataclass
class AQIData:
    european_aqi: Optional[int] = None
    us_aqi: Optional[int] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    ozone: Optional[float] = None
    no2: Optional[float] = None


@dataclass
class WeatherReport:
    city: City
    current: CurrentWeather
    daily: list[DailyForecast] = field(default_factory=list)
    hourly: list[HourlyData] = field(default_factory=list)
    aqi: Optional[AQIData] = None
