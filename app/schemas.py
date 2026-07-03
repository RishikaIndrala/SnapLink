from pydantic import BaseModel, HttpUrl
from datetime import datetime


class URLCreateRequest(BaseModel):
    long_url: HttpUrl


class URLResponse(BaseModel):
    short_code: str
    long_url: str

    class Config:
        from_attributes = True


class URLStatsResponse(BaseModel):
    short_code: str
    long_url: str
    click_count: int
    created_at: datetime

    class Config:
        from_attributes = True