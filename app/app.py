from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models, schemas, crud  # noqa: F401

app = FastAPI(
    title="SnapLink",
    description="A URL shortener built with FastAPI, iterated on via Agile micro-sprints.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "SnapLink"}


@app.post("/shorten", response_model=schemas.URLResponse)
def shorten_url(request: schemas.URLCreateRequest, db: Session = Depends(get_db)):
    db_url = crud.create_short_url(db, long_url=str(request.long_url))
    return db_url


@app.get("/stats/{short_code}", response_model=schemas.URLStatsResponse)
def get_stats(short_code: str, db: Session = Depends(get_db)):
    db_url = crud.get_url_stats(db, short_code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return db_url


@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    long_url = crud.get_url_by_code(db, short_code)
    if long_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=long_url)