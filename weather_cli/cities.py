import json
import urllib.request
import urllib.parse
from .models import City

GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"

CITIES_DB: dict[str, City] = {
    "jakarta":     City(name="Jakarta",     lat=-6.2088,  lon=106.8456, province="DKI Jakarta"),
    "surabaya":    City(name="Surabaya",    lat=-7.2575,  lon=112.7521, province="Jawa Timur"),
    "bandung":     City(name="Bandung",     lat=-6.9175,  lon=107.6191, province="Jawa Barat"),
    "medan":       City(name="Medan",       lat=3.5952,   lon=98.6722,  province="Sumatera Utara"),
    "semarang":    City(name="Semarang",    lat=-6.9932,  lon=110.4203, province="Jawa Tengah"),
    "makassar":    City(name="Makassar",    lat=-5.1477,  lon=119.4327, province="Sulawesi Selatan"),
    "yogyakarta":  City(name="Yogyakarta",  lat=-7.7956,  lon=110.3695, province="DI Yogyakarta"),
    "palembang":   City(name="Palembang",   lat=-2.9761,  lon=104.7754, province="Sumatera Selatan"),
    "denpasar":    City(name="Denpasar",    lat=-8.6705,  lon=115.2126, province="Bali"),
    "serang":      City(name="Serang",      lat=-6.1204,  lon=106.1502, province="Banten"),
    "pekanbaru":   City(name="Pekanbaru",   lat=0.5333,   lon=101.4500, province="Riau"),
    "banjarmasin": City(name="Banjarmasin", lat=-3.3197,  lon=114.5890, province="Kalimantan Selatan"),
    "manado":      City(name="Manado",      lat=1.4931,   lon=124.8413, province="Sulawesi Utara"),
    "padang":      City(name="Padang",      lat=-0.9471,  lon=100.4172, province="Sumatera Barat"),
    "pontianak":   City(name="Pontianak",   lat=-0.0263,  lon=109.3425, province="Kalimantan Barat"),
    "aceh":        City(name="Banda Aceh",  lat=5.5500,   lon=95.3175,  province="Aceh"),
    "malang":      City(name="Malang",      lat=-7.9666,  lon=112.6326, province="Jawa Timur"),
    "balikpapan":  City(name="Balikpapan",  lat=-1.2379,  lon=116.8529, province="Kalimantan Timur"),
    "samarinda":   City(name="Samarinda",   lat=-0.4981,  lon=117.1473, province="Kalimantan Timur"),
    "mataram":     City(name="Mataram",     lat=-8.5833,  lon=116.1167, province="Nusa Tenggara Barat"),
    "kupang":      City(name="Kupang",      lat=-10.1772, lon=123.6070, province="Nusa Tenggara Timur"),
    "ambon":       City(name="Ambon",       lat=-3.6954,  lon=128.1814, province="Maluku"),
    "jayapura":    City(name="Jayapura",    lat=-2.5337,  lon=140.7181, province="Papua"),
    "kendari":     City(name="Kendari",     lat=-3.9720,  lon=122.5151, province="Sulawesi Tenggara"),
    "palu":        City(name="Palu",        lat=-0.8986,  lon=119.8707, province="Sulawesi Tengah"),
    "gorontalo":   City(name="Gorontalo",   lat=0.5344,   lon=123.0609, province="Gorontalo"),
    "tanjungpinang":   City(name="Tanjungpinang",   lat=0.9228,  lon=104.4575, province="Kepulauan Riau"),
    "pangkalpinang":   City(name="Pangkalpinang",   lat=-2.1294, lon=106.1138, province="Bangka Belitung"),
    "bandarlampung":   City(name="Bandar Lampung",  lat=-5.4295, lon=105.2611, province="Lampung"),
    "bogor":      City(name="Bogor",       lat=-6.5946,  lon=106.7894, province="Jawa Barat"),
}


def search_local(query: str) -> list[City]:
    q = query.lower().strip()
    if q in CITIES_DB:
        return [CITIES_DB[q]]
    results = []
    for name, city in CITIES_DB.items():
        if q in name:
            results.append(city)
    return results


def geocode_remote(query: str) -> list[City]:
    url = f"{GEOCODING_API}?name={urllib.parse.quote(query)}&count=5&language=id&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "weather-cli/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        return []

    results = []
    for r in data.get("results", []):
        country = r.get("country_code", "")
        if country not in ("ID",):
            continue
        results.append(City(
            name=r["name"],
            lat=r["latitude"],
            lon=r["longitude"],
            province=r.get("admin1", ""),
            country="Indonesia",
        ))
    return results


def resolve(query: str) -> list[City]:
    results = search_local(query)
    if results:
        return results
    return geocode_remote(query)
