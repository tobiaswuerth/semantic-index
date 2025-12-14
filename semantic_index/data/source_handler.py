from typing import TYPE_CHECKING, Sequence
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, get_session, SessionFactory

if TYPE_CHECKING:
    from .source import Source


class SourceHandler(Base):
    __tablename__ = "source_handlers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

    sources: Mapped[list["Source"]] = relationship(
        "Source", back_populates="source_handler"
    )


class SourceHandlerRepository:
    def __init__(self, session_factory: SessionFactory = get_session):
        self._session_factory = session_factory

    def get_all(self) -> Sequence[SourceHandler]:
        with self._session_factory() as session:
            stmt = select(SourceHandler).order_by(SourceHandler.name)
            result = session.execute(stmt).scalars().all()
            session.expunge_all()
        return result

    def get_by_name(self, name: str) -> SourceHandler | None:
        with self._session_factory() as session:
            stmt = select(SourceHandler).where(SourceHandler.name == name)
            result = session.execute(stmt).scalar_one_or_none()
            session.expunge_all()
        return result

    def get_or_create(self, name: str) -> SourceHandler:
        with self._session_factory() as session:
            stmt = select(SourceHandler).where(SourceHandler.name == name)
            result = session.execute(stmt).scalar_one_or_none()

            if not result:
                result = SourceHandler(name=name)
                session.add(result)
                session.flush()

            session.expunge_all()
        return result
