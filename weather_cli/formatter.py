import shutil
from datetime import datetime
from .models import WeatherReport, DailyForecast, HourlyData

WMO_CODES = {
    0: ("Cerah", "☀️"),
    1: ("Cerah Berawan", "🌤"),
    2: ("Berawan Sebagian", "⛅"),
    3: ("Berawan", "☁️"),
    45: ("Berkabut", "🌫"),
    48: ("Kabut Beku", "🌫"),
    51: ("Gerimis Ringan", "🌦"),
    53: ("Gerimis Sedang", "🌦"),
    55: ("Gerimis Lebat", "🌦"),
    61: ("Hujan Ringan", "🌧"),
    63: ("Hujan Sedang", "🌧"),
    65: ("Hujan Lebat", "🌧"),
    71: ("Salju Ringan", "🌨"),
    73: ("Salju Sedang", "🌨"),
    75: ("Salju Lebat", "🌨"),
    80: ("Hujan Lokal Ringan", "🌦"),
    81: ("Hujan Lokal Sedang", "🌦"),
    82: ("Hujan Lokal Lebat", "🌧"),
    95: ("Badai Petir", "⛈"),
    96: ("Badai Petir dengan Hujan Es Ringan", "⛈"),
    99: ("Badai Petir dengan Hujan Es Lebat", "⛈"),
}

WIND_DIR = ["U", "TL", "T", "TG", "S", "BD", "B", "BL"]

COLS, _ = shutil.get_terminal_size()
SEP = "─" * COLS


def _wmo(wcode: int) -> tuple[str, str]:
    return WMO_CODES.get(wcode, ("Tidak Diketahui", "❓"))


def _wind_dir(deg: int) -> str:
    idx = round(deg / 45) % 8
    return WIND_DIR[idx]


def _temp_color(temp: float) -> str:
    if temp < 20:
        return "\033[34m"
    elif temp < 25:
        return "\033[32m"
    elif temp < 30:
        return "\033[33m"
    elif temp < 35:
        return "\033[38;5;208m"
    return "\033[31m"


def _aqi_label(val: int | None) -> str:
    if val is None:
        return "N/A"
    if val <= 20:
        return "Baik"
    elif val <= 40:
        return "Layak"
    elif val <= 60:
        return "Sedang"
    elif val <= 80:
        return "Kurang Sehat"
    elif val <= 100:
        return "Tidak Sehat"
    return "Berbahaya"


def _aqi_color(val: int | None) -> str:
    if val is None:
        return "\033[90m"
    if val <= 20:
        return "\033[32m"
    elif val <= 40:
        return "\033[33m"
    elif val <= 60:
        return "\033[38;5;208m"
    elif val <= 80:
        return "\033[31m"
    return "\033[35m"


def _sparkline(values: list[float], width: int = 20) -> str:
    if not values:
        return ""
    mn, mx = min(values), max(values)
    rng = mx - mn if mx != mn else 1
    bars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    line = ""
    step = max(1, len(values) // width)
    sampled = values[::step][:width]
    for v in sampled:
        idx = int((v - mn) / rng * (len(bars) - 1))
        line += bars[idx]
    return f"{mn:.0f}° {line} {mx:.0f}°"


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def _reset() -> str:
    return "\033[0m"


def format_report(report: WeatherReport, show_hourly: bool = False, no_color: bool = False) -> str:
    lines = []
    city = report.city
    cur = report.current

    desc, icon = _wmo(cur.weather_code)
    tc = "" if no_color else _temp_color(cur.temp)
    nc = "" if no_color else _reset()

    lines.append("")
    lines.append(f"  {_bold(f'{icon} {city.label}')}")
    lines.append(f"  {_dim(f'{city.country}')}")
    lines.append("")
    lines.append(f"  {tc}{_bold(f'{cur.temp:.0f}°C')}{nc}  Terasa {cur.feels_like:.0f}°C  |  {desc}")
    lines.append("")
    lines.append(f"    Kelembaban  : {cur.humidity}%")
    lines.append(f"    Angin       : {cur.wind_speed:.1f} km/jam ({_wind_dir(cur.wind_dir)})")
    lines.append(f"    Curah Hujan : {cur.precip:.1f} mm")
    lines.append(f"    Terakhir    : {cur.time}")
    lines.append("")

    if report.daily:
        lines.append(f"  {_bold('📅 Prakiraan Harian')}")
        lines.append("")
        for d in report.daily:
            ddesc, dicon = _wmo(d.weather_code)
            tcmax = "" if no_color else _temp_color(d.temp_max)
            tcmin = "" if no_color else _temp_color(d.temp_min)
            lines.append(
                f"    {_bold(d.date)}  {dicon}  "
                f"{tcmax}{d.temp_max:.0f}°{nc} / {tcmin}{d.temp_min:.0f}°{nc}  "
                f"{ddesc}  |  {_dim(f'💧{d.precip_sum:.0f}mm ☀️{d.uv_max:.1f}')}"
            )
        lines.append("")

    if show_hourly and report.hourly:
        lines.append(f"  {_bold('⏰ Per-Jam (hari ini)')}")
        lines.append("")
        temps = [h.temp for h in report.hourly[:24]]
        if temps:
            lines.append(f"    {_sparkline(temps)}")
        header = f"    {'Jam':>5} {'Suhu':>6} {'Hujan':>6} {'Angin':>5} {'Cuaca'}"
        lines.append(header)
        lines.append(f"    {'─' * (COLS - 4)}")
        for h in report.hourly[:24]:
            hdesc, hicon = _wmo(h.weather_code)
            ht = h.time.split("T")[1][:5] if "T" in h.time else h.time
            tc = "" if no_color else _temp_color(h.temp)
            lines.append(
                f"    {ht:>5} {tc}{h.temp:>5.0f}°C{nc} "
                f"{h.precip_prob:>5d}% {h.wind_speed:>4.0f} "
                f"{hicon} {hdesc}"
            )
        lines.append("")

    if report.aqi and report.aqi.european_aqi is not None:
        aqi = report.aqi
        ac = "" if no_color else _aqi_color(aqi.european_aqi)
        lines.append(f"  {_bold('🌬️ Kualitas Udara')}")
        lines.append("")
        lines.append(f"    Indeks Eropa   : {ac}{aqi.european_aqi}{nc} ({_aqi_label(aqi.european_aqi)})")
        lines.append(f"    Indeks US      : {aqi.us_aqi or 'N/A'} ({_aqi_label(aqi.us_aqi)})")
        lines.append(f"    PM2.5          : {aqi.pm25 or 'N/A'} µg/m³")
        lines.append(f"    PM10           : {aqi.pm10 or 'N/A'} µg/m³")
        lines.append(f"    Ozon           : {aqi.ozone or 'N/A'} µg/m³")
        lines.append(f"    NO2            : {aqi.no2 or 'N/A'} µg/m³")
        lines.append("")

    lines.append(_dim(f"  Sumber: Open-Meteo | weather-cli v2"))
    lines.append("")

    return "\n".join(lines)


def format_comparison(reports: list[WeatherReport], no_color: bool = False) -> str:
    lines = []
    nc = "" if no_color else _reset()
    lines.append(f"\n  {_bold('📊 Perbandingan Cuaca')}\n")

    header = f"    {'Kota':<18} {'Suhu':>8} {'Terasa':>8} {'Hum':>5} {'Angin':>8} {'Cuaca'}"
    lines.append(header)
    lines.append(f"    {'─' * (COLS - 4)}")

    for r in reports:
        desc, icon = _wmo(r.current.weather_code)
        tc = "" if no_color else _temp_color(r.current.temp)
        lines.append(
            f"    {r.city.name:<18} "
            f"{tc}{r.current.temp:>6.0f}°C{nc} "
            f"{r.current.feels_like:>6.0f}°C "
            f"{r.current.humidity:>4d}% "
            f"{r.current.wind_speed:>5.0f} km/j "
            f"{icon} {desc}"
        )
    lines.append("")
    return "\n".join(lines)


def format_json(report: WeatherReport) -> str:
    import json as _json

    def _d(obj):
        return _json.dumps(obj, indent=2, ensure_ascii=False, default=str)

    data = {
        "kota": report.city.name,
        "provinsi": report.city.province,
        "negara": report.city.country,
        "saat_ini": {
            "suhu": report.current.temp,
            "terasa": report.current.feels_like,
            "kelembaban": report.current.humidity,
            "curah_hujan": report.current.precip,
            "kecepatan_angin": report.current.wind_speed,
            "arah_angin": f"{report.current.wind_dir}°",
            "kode_cuaca": report.current.weather_code,
            "waktu": report.current.time,
        },
        "prakiraan": [
            {
                "tanggal": d.date,
                "suhu_maks": d.temp_max,
                "suhu_min": d.temp_min,
                "kode_cuaca": d.weather_code,
                "curah_hujan": d.precip_sum,
                "terbit": d.sunrise,
                "terbenam": d.sunset,
                "uv_index": d.uv_max,
            }
            for d in report.daily
        ],
    }
    if report.aqi and report.aqi.european_aqi is not None:
        data["kualitas_udara"] = {
            "indeks_eropa": report.aqi.european_aqi,
            "indeks_us": report.aqi.us_aqi,
            "pm2_5": report.aqi.pm25,
            "pm10": report.aqi.pm10,
            "ozon": report.aqi.ozone,
            "no2": report.aqi.no2,
        }
    return _d(data)


def format_csv(report: WeatherReport) -> str:
    lines = ["tanggal,suhu_min,suhu_maks,kode_cuaca,curah_hujan_mm,uv_index"]
    for d in report.daily:
        lines.append(f"{d.date},{d.temp_min},{d.temp_max},{d.weather_code},{d.precip_sum},{d.uv_max}")
    return "\n".join(lines)
