from pydantic import BaseModel

from .schema import TagSchema


class TagCount(BaseModel):
    tag: TagSchema
    count: int
