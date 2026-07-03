import random
import string
from sqlalchemy.orm import Session
from app.models import URL
from app.cache import get_cached_url, set_cached_url

CODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits


def generate_short_code() -> str:
    return "".join(random.choices(ALPHABET, k=CODE_LENGTH))


def create_short_url(db: Session, long_url: str) -> URL:
    while True:
        code = generate_short_code()
        existing = db.query(URL).filter(URL.short_code == code).first()
        if not existing:
            break

    db_url = URL(short_code=code, long_url=long_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # Populate the cache immediately on creation, so the very first
    # redirect is already a cache hit instead of a guaranteed miss.
    set_cached_url(db_url.short_code, db_url.long_url)

    return db_url


def get_url_by_code(db: Session, short_code: str) -> str | None:
    """
    Read-through cache pattern:
    1. Check Redis first (fast path)
    2. On a miss, fall back to Postgres
    3. On a DB hit, populate the cache for next time
    4. Return just the long_url string (caller doesn't need to know
       whether it came from cache or DB)
    """
    cached_url = get_cached_url(short_code)
    if cached_url:
        return cached_url  # cache hit — no DB touched at all

    db_url = db.query(URL).filter(URL.short_code == short_code).first()
    if db_url is None:
        return None  # genuinely doesn't exist

    set_cached_url(db_url.short_code, db_url.long_url)  # populate cache for next time
    return db_url.long_url