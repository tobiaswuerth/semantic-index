from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from .tag_schema import TagSchema


class SourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uri: str
    resolved_to: Optional[str] = None
    tags: list[TagSchema] = []

    obj_created: datetime
    obj_modified: datetime
    last_checked: datetime
    last_processed: datetime
    title: Optional[str] = None
