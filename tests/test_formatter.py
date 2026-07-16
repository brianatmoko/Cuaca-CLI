from weather_cli.formatter import (
    WMO_CODES,
    _temp_color,
    _aqi_label,
    _aqi_color,
    _wind_dir,
)


def test_wmo_codes():
    assert WMO_CODES[0] == ("Cerah", "☀️")
    assert WMO_CODES[95][0] == "Badai Petir"
    assert WMO_CODES[99][0] == "Badai Petir dengan Hujan Es Lebat"


def test_wmo_unknown():
    assert WMO_CODES.get(999, ("Tidak Diketahui", "❓"))[0] == "Tidak Diketahui"


def test_temp_color_cold():
    assert "34m" in _temp_color(10)  # Blue


def test_temp_color_hot():
    assert "31m" in _temp_color(36)  # Red


def test_temp_color_moderate():
    assert "32m" in _temp_color(24)  # Green


def test_aqi_label_good():
    assert _aqi_label(10) == "Baik"


def test_aqi_label_hazardous():
    assert _aqi_label(150) == "Berbahaya"


def test_aqi_label_none():
    assert _aqi_label(None) == "N/A"


def test_wind_dir():
    assert _wind_dir(0) == "U"
    assert _wind_dir(90) == "T"
    assert _wind_dir(180) == "S"
    assert _wind_dir(270) == "B"
