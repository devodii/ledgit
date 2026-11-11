from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from receipts.settings import get_settings


class Base(DeclarativeBase):
    pass


def make_engine(url: str | None = None):  # type: ignore[no-untyped-def]
    return create_engine(url or get_settings().database_url, pool_pre_ping=True)


_session_factory: sessionmaker[Session] | None = None


def get_session() -> Iterator[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(make_engine(), expire_on_commit=False)
    with _session_factory() as session:
        yield session
