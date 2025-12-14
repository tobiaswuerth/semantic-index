from typing import Sequence, TYPE_CHECKING, List
from sqlalchemy import Integer, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, get_session, SessionFactory
from .source_tag import SourceTag
from ..api import TagCount, TagSchema

if TYPE_CHECKING:
    from .source import Source


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    sources: Mapped[list["Source"]] = relationship(
        "Source", secondary=SourceTag, back_populates="tags"
    )


class TagRepository:
    def __init__(self, session_factory: SessionFactory = get_session):
        self._session_factory = session_factory

    def get_all(self) -> Sequence[Tag]:
        with self._session_factory() as session:
            stmt = select(Tag).order_by(Tag.name)
            result = session.execute(stmt).scalars().all()
            session.expunge_all()
        return result

    def get_or_create(self, name: str) -> Tag:
        with self._session_factory() as session:
            stmt = select(Tag).where(Tag.name == name)
            result = session.execute(stmt).scalar_one_or_none()
            if result is None:
                result = Tag(name=name)
                session.add(result)
                session.commit()
                session.refresh(result)
                assert result.id is not None
            session.expunge_all()
        return result

    def get_counted(self) -> List[TagCount]:
        with self._session_factory() as session:
            from .source import Source  # avoid circular import
            from .embedding import Embedding  # avoid circular import
            from .source_tag import SourceTag  # avoid circular import

            count_column = func.count(func.distinct(Source.id)).label("count")
            stmt = (
                select(Tag, count_column)
                .select_from(Tag)
                .join(SourceTag, Tag.id == SourceTag.c.tag_id)
                .join(Source, Source.id == SourceTag.c.source_id)
                .join(Embedding, Embedding.source_id == Source.id)
                .group_by(Tag.id)
                .order_by(count_column.desc())
            )
            results = session.execute(stmt).all()
            session.expunge_all()
        return [
            TagCount(
                tag=TagSchema.model_validate(tag),
                count=count,
            )
            for tag, count in results
        ]
