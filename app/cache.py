import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

# decode_responses=True means Redis returns plain Python strings instead
# of raw bytes — saves us from manually decoding every value we read.
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

CACHE_TTL_SECONDS = 3600  # cached entries expire after 1 hour


def get_cached_url(short_code: str) -> str | None:
    """Returns the cached long_url for a short_code, or None on a cache miss."""
    return redis_client.get(short_code)


def set_cached_url(short_code: str, long_url: str) -> None:
    """Stores short_code -> long_url in Redis with an expiry (TTL)."""
    redis_client.set(short_code, long_url, ex=CACHE_TTL_SECONDS)