from pydantic import BaseModel

from .schema import SourceSchema, EmbeddingSchema


class SearchResponse(BaseModel):
    source: SourceSchema
    embedding: EmbeddingSchema
    similarity: float
