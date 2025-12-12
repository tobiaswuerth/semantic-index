from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from .source_type_schema import SourceTypeSchema


class SourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: SourceTypeSchema

    uri: str
    resolved_to: Optional[str] = None

    obj_created: datetime
    obj_modified: datetime
    last_checked: datetime
    last_processed: datetime
    title: Optional[str] = None
