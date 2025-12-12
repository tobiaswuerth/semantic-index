from pydantic import BaseModel, Field, field_validator

from .search_date_filter import SearchDateFilter


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    date_filter: SearchDateFilter = Field()

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v
