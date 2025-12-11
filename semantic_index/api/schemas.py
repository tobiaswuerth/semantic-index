from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceHandlerSchema(BaseModel):
    """Schema for source handler representation."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SourceTypeSchema(BaseModel):
    """Schema for source type representation."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source_handler_id: int


class SourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_handler: SourceHandlerSchema
    source_type: SourceTypeSchema

    uri: str
    resolved_to: Optional[str] = None

    obj_created: datetime
    obj_modified: datetime
    last_checked: datetime
    last_processed: datetime
    title: Optional[str] = None


class SearchResultSchema(BaseModel):
    source: SourceSchema
    similarity: float
    embedding_id: int


class ContentSchema(BaseModel):
    section: str


class SearchQueryRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=100)

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v
