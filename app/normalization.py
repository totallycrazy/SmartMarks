"""Utilities for normalizing bookmark URLs."""
from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

TRACKING_QUERY_PATTERNS = [
    re.compile(r"^utm_", re.IGNORECASE),
    re.compile(r"^fbclid$", re.IGNORECASE),
    re.compile(r"^gclid$", re.IGNORECASE),
]


def _remove_tracking_params(query: str) -> str:
    if not query:
        return ""

    filtered_parts = []
    for part in query.split("&"):
        if not part:
            continue
        key = part.split("=", 1)[0]
        if any(pattern.match(key) for pattern in TRACKING_QUERY_PATTERNS):
            continue
        filtered_parts.append(part)
    return "&".join(filtered_parts)


def normalize_url(url: str) -> str:
    """Normalize the provided URL for deduplication purposes."""
    if not url:
        raise ValueError("URL cannot be empty")

    parts = urlsplit(url.strip())
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]

    path = parts.path.rstrip("/") or "/"
    query = _remove_tracking_params(parts.query)

    normalized = urlunsplit((
        parts.scheme.lower() or "https",
        netloc,
        path,
        query,
        "",
    ))
    return normalized
