import random
import string
from sqlalchemy.orm import Session
from sqlalchemy import update
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

    set_cached_url(db_url.short_code, db_url.long_url)

    return db_url


def get_url_by_code(db: Session, short_code: str) -> str | None:
    """
    Read-through cache pattern, now also increments click_count on every
    redirect — regardless of whether it was a cache hit or DB hit, since
    we want an accurate count either way.
    """
    cached_url = get_cached_url(short_code)
    if cached_url:
        increment_click_count(db, short_code)
        return cached_url

    db_url = db.query(URL).filter(URL.short_code == short_code).first()
    if db_url is None:
        return None

    set_cached_url(db_url.short_code, db_url.long_url)
    increment_click_count(db, short_code)
    return db_url.long_url


def increment_click_count(db: Session, short_code: str) -> None:
    """
    Lightweight, single-column UPDATE — avoids fetching the full row
    just to bump a counter. This runs on every redirect, cached or not,
    so keeping it cheap matters.
    """
    db.execute(
        update(URL)
        .where(URL.short_code == short_code)
        .values(click_count=URL.click_count + 1)
    )
    db.commit()


def get_url_stats(db: Session, short_code: str) -> URL | None:
    """Fetches full record (including click_count) for the stats endpoint."""
    return db.query(URL).filter(URL.short_code == short_code).first()