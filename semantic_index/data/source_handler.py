from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, get_session, SessionFactory

if TYPE_CHECKING:
    from .source import Source
    from .source_type import SourceType


class SourceHandler(Base):
    __tablename__ = "source_handlers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

    source_types: Mapped[list["SourceType"]] = relationship(
        "SourceType", back_populates="source_handler"
    )
    sources: Mapped[list["Source"]] = relationship(
        "Source", back_populates="source_handler"
    )


class SourceHandlerRepository:
    def __init__(self, session_factory: SessionFactory = get_session):
        self._session_factory = session_factory

    def get_all(self) -> list[SourceHandler]:
        with self._session_factory() as session:
            handlers = list(session.execute(select(SourceHandler)).scalars().all())
            for handler in handlers:
                session.expunge(handler)
            return handlers

    def get_by_name(self, name: str) -> SourceHandler | None:
        with self._session_factory() as session:
            handler = session.execute(
                select(SourceHandler).where(SourceHandler.name == name)
            ).scalar_one_or_none()
            if handler:
                session.expunge(handler)
            return handler

    def get_or_create(self, name: str) -> SourceHandler:
        with self._session_factory() as session:
            handler = session.execute(
                select(SourceHandler).where(SourceHandler.name == name)
            ).scalar_one_or_none()
            if handler:
                session.expunge(handler)
                return handler

            handler = SourceHandler(name=name)
            session.add(handler)
            session.flush()
            session.expunge(handler)
            return handler
