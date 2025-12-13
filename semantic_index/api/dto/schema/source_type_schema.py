from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class SourceTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source_handler_id: int
    contains: Optional[List[str]] = None
