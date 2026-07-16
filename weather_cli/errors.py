class WeatherError(Exception):
    """Base exception for weather-cli."""


class APIError(WeatherError):
    """API request failed."""


class CityNotFoundError(WeatherError):
    """City could not be resolved."""


class ConfigError(WeatherError):
    """Configuration error."""


class NetworkError(APIError):
    """Network connectivity issue."""


class RateLimitError(APIError):
    """API rate limit exceeded."""


ERROR_MESSAGES = {
    "connection": (
        "Tidak dapat terhubung ke server cuaca.\n"
        "  Periksa koneksi internet Anda."
    ),
    "timeout": (
        "Koneksi timeout. Server terlalu lambat.\n"
        "  Coba lagi dalam beberapa saat."
    ),
    "city": (
        "Kota tidak ditemukan.\n"
        "  Coba gunakan nama kota yang lebih spesifik."
    ),
    "api": (
        "Gagal mengambil data cuaca.\n"
        "  Coba lagi dalam beberapa saat."
    ),
}
