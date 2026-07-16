import argparse
import sys
import os
from . import __version__
from .config import load as load_config, save as save_config
from .config import load_favorites, save_favorites
from .cities import resolve
from .api import fetch_weather, fetch_aqi, parse_current, parse_daily, parse_hourly, parse_aqi
from .models import WeatherReport, City
from .formatter import format_report, format_comparison, format_json, format_csv
from .geoip import detect_city
from .cache import cache_cleanup, cache_stats
from .errors import APIError, CityNotFoundError, NetworkError, WeatherError, ERROR_MESSAGES

VERBOSE = False


def log(msg: str):
    if VERBOSE:
        print(f"  [debug] {msg}", file=sys.stderr)


def _resolve_city(query: str, config: dict) -> City | None:
    log(f"Resolving city: {query}")
    results = resolve(query)
    if not results:
        return None
    if len(results) == 1:
        return results[0]
    print(f"\n  Banyak kota ditemukan untuk '{query}':\n")
    for i, c in enumerate(results):
        print(f"    {i+1}. {c.label}")
    try:
        choice = int(input("\n  Pilih nomor: ")) - 1
        return results[choice] if 0 <= choice < len(results) else results[0]
    except (ValueError, IndexError, EOFError):
        return results[0]


def _get_city(args, config: dict) -> City | None:
    if args.city:
        return _resolve_city(args.city, config)
    favs = load_favorites()
    if favs:
        log(f"Using favorite: {favs[0]}")
        return _resolve_city(favs[0], config)
    geo = detect_city()
    if geo:
        log(f"GeoIP detected: {geo.name}")
        return geo
    return _resolve_city(config.get("default_city", "Jakarta"), config)


def main() -> int:
    global VERBOSE
    config = load_config()

    parser = argparse.ArgumentParser(
        prog="weather",
        description="Cek cuaca Indonesia dari terminal",
        epilog="Contoh: weather Bandung --forecast 5 --aqi",
    )
    parser.add_argument("city", nargs="?", help="Nama kota")
    parser.add_argument("-f", "--forecast", type=int, nargs="?", const=0, default=0,
                        help="Prakiraan N hari (default: 3)")
    parser.add_argument("--hourly", action="store_true", help="Tampilkan per-jam")
    parser.add_argument("--aqi", action="store_true", help="Tampilkan kualitas udara")
    parser.add_argument("-c", "--compare", nargs="+", metavar="KOTA",
                        help="Bandingkan dengan kota lain")
    parser.add_argument("--save", action="store_true", help="Simpan kota ke favorit")
    parser.add_argument("--favorites", action="store_true", help="Lihat kota favorit")
    parser.add_argument("--export", choices=("json", "csv"), help="Export format")
    parser.add_argument("--config", nargs=1, metavar="KEY=VAL",
                        help="Set konfigurasi (contoh: default_city=Bandung)")
    parser.add_argument("--no-color", action="store_true", help="Nonaktifkan warna")
    parser.add_argument("--verbose", "-v", action="store_true", help="Tampilkan debug log")
    parser.add_argument("--version", action="store_true", help="Tampilkan versi")
    parser.add_argument("--cache-cleanup", action="store_true",
                        help="Bersihkan cache (hapus file >24 jam)")

    args = parser.parse_args()

    if args.verbose:
        VERBOSE = True

    if args.version:
        print(f"weather-cli v{__version__}")
        return 0

    if args.cache_cleanup:
        removed = cache_cleanup()
        stats = cache_stats()
        print(f"  Cache dibersihkan: {removed} file dihapus")
        print(f"  Cache saat ini: {stats['files']} file ({stats['size_kb']} KB)")
        return 0

    if args.config:
        kv = args.config[0]
        if "=" in kv:
            key, val = kv.split("=", 1)
            config[key] = val
            save_config(config)
            print(f"  Konfigurasi {key} = {val} disimpan")
            return 0
        print("  Format: --config key=value")
        return 1

    if args.favorites:
        favs = load_favorites()
        if not favs:
            print("  Belum ada kota favorit. Gunakan --save untuk menambahkan.")
            return 0
        print(f"\n  Kota Favorit")
        for f in favs:
            print(f"    \u2022 {f}")
        print()
        return 0

    forecast_days = args.forecast
    if forecast_days == 0:
        forecast_days = config.get("forecast_days", 3)

    try:
        if args.compare:
            return _handle_compare(args, config)

        city = _get_city(args, config)
        if not city:
            msg = ERROR_MESSAGES["city"]
            print(f"  Kota '{args.city or config['default_city']}' tidak ditemukan")
            return 1

        if args.save:
            favs = load_favorites()
            if city.name not in favs:
                favs.append(city.name)
                save_favorites(favs)
                print(f"  {city.name} ditambahkan ke favorit!")
            else:
                print(f"  {city.name} sudah ada di favorit")
            return 0

        raw = fetch_weather(city, forecast_days, hourly=args.hourly)
        log(f"Weather data received for {city.name}")
        current = parse_current(raw)
        daily = parse_daily(raw)
        hourly = parse_hourly(raw) if args.hourly else []
        aqi = parse_aqi(fetch_aqi(city)) if args.aqi else None

        report = WeatherReport(
            city=city,
            current=current,
            daily=daily,
            hourly=hourly,
            aqi=aqi,
        )

        if args.export == "json":
            print(format_json(report))
        elif args.export == "csv":
            print(format_csv(report))
        else:
            print(format_report(report, show_hourly=args.hourly, no_color=args.no_color))

        return 0

    except NetworkError:
        print(f"\n  {ERROR_MESSAGES['connection']}\n")
        return 1
    except APIError as e:
        print(f"\n  Gagal mengambil data cuaca.")
        if VERBOSE:
            print(f"  {e}")
        print(f"  Coba lagi dalam beberapa saat.\n")
        return 1
    except WeatherError as e:
        print(f"\n  Error: {e}\n")
        return 1


def _handle_compare(args, config: dict) -> int:
    cities = []
    for q in [args.city] + args.compare:
        if not q:
            continue
        c = _resolve_city(q, config)
        if c:
            cities.append(c)
        else:
            print(f"  Kota '{q}' tidak ditemukan")
            return 1
    if len(cities) < 2:
        print("  Minimal 2 kota untuk perbandingan")
        return 1
    reports = []
    for c in cities:
        raw = fetch_weather(c, 1)
        current = parse_current(raw)
        reports.append(WeatherReport(city=c, current=current))
    print(format_comparison(reports, no_color=args.no_color))
    return 0


if __name__ == "__main__":
    sys.exit(main())
