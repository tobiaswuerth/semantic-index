from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uri: str
    last_modified: datetime
    last_processed: Optional[datetime] = None
    error: bool = False
    error_message: Optional[str] = None


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
