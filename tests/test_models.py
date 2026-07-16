from weather_cli.models import City, CurrentWeather, DailyForecast, HourlyData, AQIData, WeatherReport


def test_city_label():
    city = City(name="Jakarta", lat=-6.2, lon=106.8, province="DKI Jakarta")
    assert city.label == "Jakarta, DKI Jakarta"


def test_city_label_no_province():
    city = City(name="Tokyo", lat=35.6, lon=139.6, country="Japan")
    assert city.label == "Tokyo"


def test_current_weather_defaults():
    cw = CurrentWeather(
        temp=30.0, feels_like=32.0, humidity=70,
        precip=0.0, wind_speed=10.0, wind_dir=180,
        weather_code=0, time="2026-07-16T12:00",
    )
    assert cw.temp == 30.0
    assert cw.humidity == 70
    assert cw.weather_code == 0


def test_daily_forecast():
    df = DailyForecast(
        date="2026-07-16", temp_max=32.0, temp_min=24.0,
        weather_code=1, precip_sum=0.5,
        sunrise="06:00", sunset="18:00", uv_max=7.0,
        wind_speed=15.0,
    )
    assert df.temp_max == 32.0
    assert df.precip_sum == 0.5


def test_hourly_data():
    hd = HourlyData(
        time="2026-07-16T13:00", temp=31.0,
        precip_prob=10, weather_code=0, wind_speed=12.0,
    )
    assert hd.temp == 31.0
    assert hd.precip_prob == 10


def test_aqi_empty():
    aqi = AQIData()
    assert aqi.european_aqi is None
    assert aqi.us_aqi is None


def test_aqi_full():
    aqi = AQIData(european_aqi=25, us_aqi=30, pm25=10.5, pm10=20.0, ozone=80.0, no2=15.0)
    assert aqi.european_aqi == 25
    assert aqi.pm25 == 10.5


def test_weather_report():
    city = City(name="Jakarta", lat=-6.2, lon=106.8)
    cw = CurrentWeather(30.0, 32.0, 70, 0.0, 10.0, 180, 0, "2026-07-16T12:00")
    report = WeatherReport(city=city, current=cw)
    assert report.city.name == "Jakarta"
    assert report.current.temp == 30.0
    assert report.daily == []
    assert report.hourly == []
    assert report.aqi is None
