from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class TagSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contains: Optional[List[str]] = None
