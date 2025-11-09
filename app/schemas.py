"""Pydantic schemas for API payloads."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator

from .normalization import normalize_url


class BookmarkBase(BaseModel):
    url: HttpUrl
    title: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    reading_time_minutes: Optional[int] = None
    content_type: Optional[str] = None
    language: Optional[str] = None

    @validator("tags", pre=True, always=True)
    def ensure_tags(cls, value: Optional[List[str]]) -> List[str]:
        if value is None:
            return []
        return value


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    reading_time_minutes: Optional[int] = None
    content_type: Optional[str] = None
    language: Optional[str] = None


class Bookmark(BookmarkBase):
    id: int
    normalized_url: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class BookmarkImportSummary(BaseModel):
    imported: int
    skipped_duplicates: int


class BookmarkInternal(BaseModel):
    """Internal schema used for persistence."""

    url: str
    normalized_url: str
    title: str
    description: Optional[str]
    tags: str
    source: Optional[str]
    reading_time_minutes: Optional[int]
    content_type: Optional[str]
    language: Optional[str]

    @classmethod
    def from_create(cls, payload: BookmarkCreate) -> "BookmarkInternal":
        return cls(
            url=str(payload.url),
            normalized_url=normalize_url(str(payload.url)),
            title=payload.title,
            description=payload.description,
            tags=",".join(sorted(set(payload.tags))),
            source=payload.source,
            reading_time_minutes=payload.reading_time_minutes,
            content_type=payload.content_type,
            language=payload.language,
        )
