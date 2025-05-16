from fastapi import FastAPI
from pydantic import BaseModel, field_validator

from semantic_index import GTEEmbeddingModel, exception_handled_json_api

embedding_model: GTEEmbeddingModel = GTEEmbeddingModel()
app = FastAPI()


class EmbeddingRequest(BaseModel):
    batch: list[str]

    @field_validator("batch")
    def batch_not_empty(cls, v):
        if not v:
            raise ValueError("Batch cannot be empty")
        return v


@app.post("/generate_embedding")
@exception_handled_json_api
async def generate_embedding(request: EmbeddingRequest):
    return embedding_model._encode_batch(request.batch).tolist()


# To run: uvicorn embedding_factory:app --host 0.0.0.0 --port 8000
