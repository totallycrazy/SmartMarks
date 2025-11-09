# AtlasBookmarks (SmartMarks)

AtlasBookmarks is an early implementation of the "Next-Level Bookmark Management" platform described in the [product requirements document](docs/next-level-bookmark-management-prd.md). This initial iteration focuses on foundational capabilities so that future work can expand into enrichment, analytics, and workflow automation.

## Getting Started

### Prerequisites
* Python 3.11+
* `pip`

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the API

```bash
uvicorn app.main:app --reload
```

The API exposes CRUD endpoints under `/bookmarks` and an HTML import endpoint under `/imports/html`.

### Importing from HTML

```bash
python scripts/import_html.py path/to/bookmarks.html
```

### Testing

```bash
pytest
```

## Roadmap Alignment

This codebase establishes key scaffolding:

* Normalized bookmark persistence with duplicate detection aligning with the PRD's ingestion and deduplication goals.
* Parsers for Netscape-style HTML exports as a first ingestion surface.
* REST API endpoints supporting creation, retrieval, updates, and deletions of bookmarks as a foundation for dashboard experiences.

Future milestones will layer in background processing, enrichment pipelines, and integrations described throughout the PRD.
