import random
import string
from sqlalchemy.orm import Session
from app.models import URL

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
    return db_url


def get_url_by_code(db: Session, short_code: str) -> URL | None:
    return db.query(URL).filter(URL.short_code == short_code).first()