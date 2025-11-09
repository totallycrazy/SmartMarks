"""CRUD helpers for bookmark operations."""
from __future__ import annotations

from typing import Iterable, List, Optional

from sqlalchemy.orm import Session

from . import models
from .normalization import normalize_url
from .schemas import BookmarkCreate, BookmarkInternal, BookmarkUpdate


def get_bookmarks(session: Session, skip: int = 0, limit: int = 100) -> List[models.Bookmark]:
    query = session.query(models.Bookmark).order_by(models.Bookmark.created_at.desc())
    return query.offset(skip).limit(limit).all()


def get_bookmark(session: Session, bookmark_id: int) -> Optional[models.Bookmark]:
    return session.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()


def get_bookmark_by_url(session: Session, url: str) -> Optional[models.Bookmark]:
    normalized = normalize_url(url)
    return (
        session.query(models.Bookmark)
        .filter(models.Bookmark.normalized_url == normalized)
        .first()
    )


def _update_model(instance: models.Bookmark, payload: BookmarkUpdate) -> models.Bookmark:
    for field, value in payload.dict(exclude_unset=True).items():
        if field == "tags" and value is not None:
            setattr(instance, field, ",".join(sorted(set(value))))
        else:
            setattr(instance, field, value)
    return instance


def create_bookmark(session: Session, payload: BookmarkCreate) -> models.Bookmark:
    existing = get_bookmark_by_url(session, str(payload.url))
    if existing:
        return existing

    internal = BookmarkInternal.from_create(payload)
    bookmark = models.Bookmark(**internal.dict())
    session.add(bookmark)
    session.flush()
    return bookmark


def update_bookmark(
    session: Session, bookmark_id: int, payload: BookmarkUpdate
) -> Optional[models.Bookmark]:
    bookmark = get_bookmark(session, bookmark_id)
    if not bookmark:
        return None
    bookmark = _update_model(bookmark, payload)
    session.add(bookmark)
    session.flush()
    return bookmark


def delete_bookmark(session: Session, bookmark_id: int) -> bool:
    bookmark = get_bookmark(session, bookmark_id)
    if not bookmark:
        return False
    session.delete(bookmark)
    session.flush()
    return True


def bulk_create_bookmarks(
    session: Session, payloads: Iterable[BookmarkCreate]
) -> tuple[int, int]:
    imported = 0
    skipped = 0
    for payload in payloads:
        existing = get_bookmark_by_url(session, str(payload.url))
        if existing:
            skipped += 1
            continue
        bookmark = models.Bookmark(**BookmarkInternal.from_create(payload).dict())
        session.add(bookmark)
        imported += 1
    session.flush()
    return imported, skipped
