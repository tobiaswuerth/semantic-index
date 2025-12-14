from sqlalchemy import ForeignKey, Integer, Column, Table

from .database import Base


SourceTag = Table(
    "sources_tags",
    Base.metadata,
    Column("source_id", Integer, ForeignKey("sources.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)
