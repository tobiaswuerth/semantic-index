from pydantic import BaseModel, ConfigDict


class EmbeddingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    chunk_idx: int
