from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class URL(Base):
    """
    Core table for SnapLink: maps a short_code to its original long_url.

    click_count and created_at are included now (not used yet) because
    adding columns later means a migration — cheaper to reserve the
    shape of the table today than to alter it after data exists.
    """
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(10), unique=True, index=True, nullable=False)
    long_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    click_count = Column(Integer, default=0)