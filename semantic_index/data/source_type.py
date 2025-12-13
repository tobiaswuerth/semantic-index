from typing import TYPE_CHECKING, Sequence
from sqlalchemy import Integer, String, ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..api import SourceTypeCount, SourceTypeSchema
from .database import Base, get_session, SessionFactory

if TYPE_CHECKING:
    from .source import Source
    from .source_handler import SourceHandler


class SourceType(Base):
    __tablename__ = "source_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

    source_handler_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("source_handlers.id"), nullable=False
    )
    source_handler: Mapped["SourceHandler"] = relationship(
        "SourceHandler", back_populates="source_types"
    )

    sources: Mapped[list["Source"]] = relationship(
        "Source", back_populates="source_type"
    )


class SourceTypeRepository:
    def __init__(self, session_factory: SessionFactory = get_session):
        self._session_factory = session_factory

    def get_all(self) -> Sequence[SourceType]:
        with self._session_factory() as session:
            stmt = select(SourceType).order_by(SourceType.name)
            result = session.execute(stmt).scalars().all()
            session.expunge_all()
        return result

    def get_all_counted(self) -> list[SourceTypeCount]:
        from .source import Source  # avoid circular import
        from .embedding import Embedding  # avoid circular import

        with self._session_factory() as session:
            stmt = (
                select(SourceType, func.count(func.distinct(Embedding.source_id)))
                .select_from(SourceType)
                .outerjoin(Source, Source.source_type_id == SourceType.id)
                .outerjoin(Embedding, Embedding.source_id == Source.id)
                .group_by(SourceType.id)
                .order_by(SourceType.name)
            )
            results = session.execute(stmt).all()
            session.expunge_all()

        return [
            SourceTypeCount(
                source_type=SourceTypeSchema.model_validate(source_type),
                count=count,
            )
            for source_type, count in results
        ]

    def get_by_name(self, name: str) -> SourceType | None:
        with self._session_factory() as session:
            stmt = select(SourceType).where(SourceType.name == name)
            result = session.execute(stmt).scalar_one_or_none()
            session.expunge_all()
        return result

    def get_or_create(self, name: str, source_handler_id: int) -> SourceType:
        with self._session_factory() as session:
            stmt = select(SourceType).where(SourceType.name == name)
            result = session.execute(stmt).scalar_one_or_none()

            if not result:
                result = SourceType(name=name, source_handler_id=source_handler_id)
                session.add(result)
                session.flush()

            session.expunge_all()
        return result
