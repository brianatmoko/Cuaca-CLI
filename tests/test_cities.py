import json
import os
from weather_cli.cities import CITIES_DB, search_local


def test_builtin_cities_exist():
    assert len(CITIES_DB) >= 30
    assert "jakarta" in CITIES_DB
    assert "bandung" in CITIES_DB
    assert "surabaya" in CITIES_DB


def test_search_local_exact():
    results = search_local("Jakarta")
    assert len(results) == 1
    assert results[0].name == "Jakarta"
    assert results[0].province == "DKI Jakarta"


def test_search_local_partial():
    results = search_local("jaka")
    assert len(results) >= 1
    assert any(c.name.lower() == "jakarta" for c in results)


def test_search_local_empty():
    results = search_local("xyznonexistent")
    assert results == []


def test_city_coordinates():
    city = CITIES_DB["bandung"]
    assert isinstance(city.lat, float)
    assert isinstance(city.lon, float)
    assert -90 <= city.lat <= 90
    assert -180 <= city.lon <= 180
