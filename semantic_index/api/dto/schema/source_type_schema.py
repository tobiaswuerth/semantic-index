from pydantic import BaseModel, ConfigDict


class SourceTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source_handler_id: int
