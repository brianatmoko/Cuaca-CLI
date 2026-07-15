# weather-cli 🌤️

CLI cuaca Indonesia — pakai data dari Open-Meteo (gratis, tanpa API key).

## Fitur

- ✅ Cuaca realtime + prakiraan hingga 7 hari
- ✅ Database 30+ kota Indonesia (offline)
- ✅ Geocoding otomatis untuk kota lain
- ✅ Deteksi lokasi otomatis via IP (ip-api.com)
- ✅ Kualitas udara (AQI) — PM2.5, PM10, Ozon, NO2
- ✅ Tampilan per-jam (24 jam ke depan)
- ✅ Warna berdasarkan suhu
- ✅ Perbandingan antar kota
- ✅ Kota favorit — simpan & lihat cepat
- ✅ Export JSON / CSV
- ✅ Cache otomatis (5 menit)
- ✅ Konfigurasi persisten (~/.config/weather-cli/)
- ✅ Zero dependensi — stdlib Python aja

## Instalasi

```bash
git clone <repo-url>
cd weather-cli
chmod +x install.sh
./install.sh
```

Pastikan `~/.local/bin` ada di PATH.

## Usage

```bash
weather                        # Cuaca Jakarta (default)
weather Bandung                # Cuaca kota tertentu
weather -f 5                   # Prakiraan 5 hari
weather --hourly               # Tampilkan per-jam
weather --aqi                  # Kualitas udara
weather -c Bandung Surabaya    # Bandingkan 2+ kota
weather --save                 # Simpan kota ke favorit
weather --favorites            # Lihat favorit
weather --export json          # Export JSON
weather --export csv           # Export CSV
weather --config default_city=Bandung
```

## Struktur Project

```
weather-cli/
├── weather_cli/          # Package Python
│   ├── __init__.py       # Version
│   ├── __main__.py       # Entry point
│   ├── cli.py            # Argparse + orchestration
│   ├── api.py            # Open-Meteo API client
│   ├── models.py         # Data classes
│   ├── formatter.py      # Output formatting
│   ├── cities.py         # Indonesian cities DB + geocoding
│   ├── config.py         # Config manager
│   ├── cache.py          # File-based TTL cache
│   └── geoip.py          # Auto-detect location by IP
├── install.sh
└── README.md
```

## Tech Stack

- **Runtime:** Python 3.12+ — zero external dependencies, stdlib only
- **API Integration:** Open-Meteo (weather, geocoding, air quality), ip-api.com (GeoIP)
- **Persistence:** JSON-based config engine + TTL cache (MD5-keyed, file-backed)
- **Output Layer:** ANSI escape codes, dynamic sparklines, multi-format rendering (human/JSON/CSV)
- **Why stdlib-only?** No pip install. No venv. No `requirements.txt`. One `git clone` away from running

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                        Presentation Layer                    │
│  cli.py (argparse, orchestration, fallback chain)           │
│  formatter.py (ANSI, JSON, CSV, comparison tables)         │
├─────────────────────────────────────────────────────────────┤
│                        Domain Layer                          │
│  models.py (6 dataclasses: City, CurrentWeather,            │
│             DailyForecast, HourlyData, AQIData,             │
│             WeatherReport)                                  │
├─────────────────────────────────────────────────────────────┤
│                     Infrastructure Layer                     │
│  api.py (HTTP client → Open-Meteo)   cities.py (30 cities DB│
│  cache.py (MD5 TTL cache)            config.py (persistence)│
│  geoip.py (ip-api.com auto-detect)                          │
└─────────────────────────────────────────────────────────────┘
```

**Architecture highlights:**

| Pattern | Implementation |
|---------|---------------|
| Chain of Responsibility | City resolution: CLI arg → favorites → GeoIP → config default |
| Cache-Aside | Every API call checks `cache_get()` before hitting the wire |
| Separated Presentation | Models never know about formatting; formatters never mutate data |
| Strategy Pattern | Three output strategies (human, JSON, CSV) selected at runtime |
| Fallback Degradation | Local city DB → remote geocoding API; GeoIP → Jakarta default |
| Front Controller | `cli.py:main()` — single entry point handles all routing |

**Data flow (single request):** `shell → argparse → city resolution → cache check → API fetch → JSON parse → model assembly → format selection → stdout`

## Core Value

**"Zero-dependency CLI yang terasa seperti native."**

| Value | Kenapa |
|-------|--------|
| **Instan** | Gak perlu `pip install`, gak perlu venv, gak perlu setup environment |
| **Offline-first** | 30 kota Indonesia built-in, cache 5 menit — hemat kuota |
| **Indonesian-first** | Terminal output pake Bahasa Indonesia, kota default Jakarta |
| **Portable** | Satu folder `weather_cli/`, jalan di mana aja ada Python 3 |
| **Transparan** | Semua data lokal: config JSON, cache JSON, favorit JSON — bisa diedit manual |
| **Developer-friendly** | Architecture bersih layered, gampang ditambah API lain atau output format baru |
