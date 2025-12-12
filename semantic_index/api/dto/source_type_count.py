from pydantic import BaseModel

from .schema import SourceTypeSchema


class SourceTypeCount(BaseModel):
    source_type: SourceTypeSchema
    count: int
