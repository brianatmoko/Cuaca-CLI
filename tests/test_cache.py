import os
import time
from weather_cli.cache import cache_get, cache_set, cache_cleanup, cache_stats


def test_cache_set_get():
    cache_set("test_key", {"temp": 30})
    result = cache_get("test_key")
    assert result == {"temp": 30}


def test_cache_expiry():
    cache_set("expire_key", "value", ttl=0)
    # Sleep briefly to ensure TTL has passed
    time.sleep(0.01)
    result = cache_get("expire_key", ttl=0)
    assert result is None


def test_cache_miss():
    result = cache_get("nonexistent_key")
    assert result is None


def test_cache_cleanup():
    cache_set("cleanup_test", "data")
    stats = cache_stats()
    assert stats["files"] > 0
    assert stats["size_kb"] > 0
