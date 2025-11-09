"""FastAPI application entry point for AtlasBookmarks."""
from __future__ import annotations

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from . import crud, models
from .database import Base, SessionLocal, engine
from .importers.html import BookmarkHtmlImporter
from .schemas import (
    Bookmark,
    BookmarkCreate,
    BookmarkImportSummary,
    BookmarkUpdate,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AtlasBookmarks", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/bookmarks", response_model=list[Bookmark])
def list_bookmarks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_bookmarks(db, skip=skip, limit=limit)


@app.post("/bookmarks", response_model=Bookmark, status_code=201)
def create_bookmark(payload: BookmarkCreate, db: Session = Depends(get_db)):
    bookmark = crud.create_bookmark(db, payload)
    return bookmark


@app.get("/bookmarks/{bookmark_id}", response_model=Bookmark)
def read_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    bookmark = crud.get_bookmark(db, bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark


@app.put("/bookmarks/{bookmark_id}", response_model=Bookmark)
def update_bookmark(bookmark_id: int, payload: BookmarkUpdate, db: Session = Depends(get_db)):
    bookmark = crud.update_bookmark(db, bookmark_id, payload)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark


@app.delete("/bookmarks/{bookmark_id}", status_code=204)
def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_bookmark(db, bookmark_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return None


@app.post("/imports/html", response_model=BookmarkImportSummary)
def import_html_bookmarks(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    raw = file.file.read().decode("utf-8")
    importer = BookmarkHtmlImporter()
    payloads = list(importer.parse(raw))
    imported, skipped = crud.bulk_create_bookmarks(db, payloads)
    return BookmarkImportSummary(imported=imported, skipped_duplicates=skipped)
