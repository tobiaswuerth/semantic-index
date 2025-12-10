import logging
from contextlib import AbstractContextManager, contextmanager
from typing import Callable, Generator
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..config import config


logger = logging.getLogger(__name__)
Base = declarative_base()
SessionFactory = Callable[[], AbstractContextManager[Session]]

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            config.database.url,
            echo=config.database.echo,
            pool_pre_ping=True,
        )
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
    from .source_handler import SourceHandler  # noqa: F401
    from .source_type import SourceType  # noqa: F401

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
