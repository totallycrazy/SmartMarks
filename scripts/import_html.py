"""CLI helper to import bookmarks from an exported HTML file."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import crud
from app.database import Base, SessionLocal, engine
from app.importers.html import BookmarkHtmlImporter
from app.schemas import BookmarkCreate

Base.metadata.create_all(bind=engine)


def _serialize_payloads(payloads: Iterable[BookmarkCreate]) -> List[dict[str, str]]:
    """Convert BookmarkCreate models into plain dictionaries for logging."""

    serialized: List[dict[str, str]] = []
    for payload in payloads:
        record = payload.dict()
        record["url"] = str(record["url"])
        record["tags"] = ", ".join(payload.tags) if payload.tags else ""
        serialized.append(record)
    return serialized


def _write_log(
    *,
    destination: Path,
    source_file: Path,
    parsed: List[dict[str, str]],
    imported: int,
    skipped: int,
) -> Path:
    """Persist the import results to a timestamped log file."""

    timestamp = datetime.now(timezone.utc)
    destination.mkdir(parents=True, exist_ok=True)
    log_path = destination / f"results_{timestamp.strftime('%y-%m-%d-%H-%M')}.log"

    lines = [
        f"Import executed at {timestamp.isoformat()}",
        f"Source file: {source_file.resolve()}",
        f"Total parsed bookmarks: {len(parsed)}",
        f"Imported records: {imported}",
        f"Skipped duplicates: {skipped}",
        "",
        "Bookmarks:",
    ]

    if not parsed:
        lines.append("  (no bookmarks parsed)")
    else:
        for index, bookmark in enumerate(parsed, start=1):
            lines.append(f"  {index}. {bookmark['title']} -> {bookmark['url']}")
            if bookmark.get("tags"):
                lines.append(f"     Tags: {bookmark['tags']}")
            if bookmark.get("description"):
                lines.append(f"     Description: {bookmark['description']}")
            if bookmark.get("source"):
                lines.append(f"     Source: {bookmark['source']}")

    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return log_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Import bookmarks from HTML export")
    parser.add_argument("path", type=Path, help="Path to the exported HTML file")
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=None,
        help="Optional directory to write a timestamped import summary log",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse the HTML without persisting bookmarks to the database",
    )
    args = parser.parse_args()

    importer = BookmarkHtmlImporter()
    payloads = importer.parse_file(str(args.path))
    serialized = _serialize_payloads(payloads)

    imported = 0
    skipped = 0
    if args.dry_run:
        imported = len(serialized)
    else:
        with SessionLocal() as session:
            imported, skipped = crud.bulk_create_bookmarks(session, payloads)
            session.commit()

    log_message = f"Imported: {imported}, skipped duplicates: {skipped}"
    print(log_message)

    if args.log_dir:
        log_path = _write_log(
            destination=args.log_dir,
            source_file=args.path,
            parsed=serialized,
            imported=imported,
            skipped=skipped,
        )
        print(f"Results written to {log_path}")


if __name__ == "__main__":
    main()
