import logging
from contextlib import AbstractContextManager, contextmanager
from typing import Callable, Generator
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..config import config


logger = logging.getLogger(__name__)
Base = declarative_base()
SessionFactory = Callable[[], AbstractContextManager[Session]]

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine:
        return _engine

    url = config.database.url
    args = {
        "url": url,
        "echo": config.database.echo,
        "pool_pre_ping": True,
    }

    # Special handling for SQLite: allow connections from multiple threads
    if url.startswith("sqlite"):
        # File-based SQLite: disable check_same_thread so connections can
        # be used in different threads (FastAPI offloads blocking work).
        args["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url:
            # In-memory SQLite needs StaticPool to be shared across threads.
            args["poolclass"] = StaticPool

    _engine = create_engine(**args)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionLocal


def init_db() -> None:
    from .embedding import Embedding  # noqa: F401
    from .source import Source  # noqa: F401
    from .source_tag import SourceTag  # noqa: F401
    from .source_handler import SourceHandler  # noqa: F401
    from .tag import Tag  # noqa: F401

    logger.info("Initializing database...")
    Base.metadata.create_all(bind=get_engine())


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
