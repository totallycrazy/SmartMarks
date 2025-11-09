"""SQLAlchemy models representing persistent entities."""
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class Bookmark(Base):
    """A saved link with enriched metadata."""

    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=False, nullable=False)
    normalized_url = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(String, nullable=True)
    source = Column(String, nullable=True)
    reading_time_minutes = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    language = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)

    def tag_list(self) -> List[str]:
        return [tag for tag in (self.tags or "").split(",") if tag]
