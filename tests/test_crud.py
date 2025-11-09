from app import crud
from app.database import Base, SessionLocal, engine
from app.schemas import BookmarkCreate, BookmarkUpdate


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_and_get_bookmark():
    reset_db()
    payload = BookmarkCreate(
        url="https://example.com/article",
        title="Example",
        tags=["research", "example"],
    )
    with SessionLocal() as session:
        bookmark = crud.create_bookmark(session, payload)
        session.commit()
        assert bookmark.id is not None

        fetched = crud.get_bookmark(session, bookmark.id)
        assert fetched.title == "Example"
        assert sorted(fetched.tag_list()) == ["example", "research"]


def test_duplicate_bookmark_returns_existing():
    reset_db()
    payload = BookmarkCreate(url="https://example.com", title="First")
    duplicate = BookmarkCreate(url="https://EXAMPLE.com/", title="Duplicate")

    with SessionLocal() as session:
        first = crud.create_bookmark(session, payload)
        second = crud.create_bookmark(session, duplicate)
        session.commit()

        assert first.id == second.id
        assert crud.get_bookmarks(session)[0].title == "First"


def test_update_and_delete_bookmark():
    reset_db()
    payload = BookmarkCreate(url="https://example.com/update", title="Update Me")
    with SessionLocal() as session:
        bookmark = crud.create_bookmark(session, payload)
        session.commit()

        updated = crud.update_bookmark(
            session, bookmark.id, BookmarkUpdate(title="Updated", tags=["new"])
        )
        session.commit()
        assert updated.title == "Updated"
        assert updated.tags == "new"

        assert crud.delete_bookmark(session, bookmark.id)
        session.commit()
        assert crud.get_bookmark(session, bookmark.id) is None
