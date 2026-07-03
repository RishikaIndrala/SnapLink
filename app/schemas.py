from pydantic import BaseModel, HttpUrl


class URLCreateRequest(BaseModel):
    long_url: HttpUrl


class URLResponse(BaseModel):
    short_code: str
    long_url: str

    class Config:
        from_attributes = True