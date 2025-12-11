from fastapi import FastAPI
from pydantic import BaseModel, field_validator

from semantic_index import GTEEmbeddingModel

app = FastAPI()
model = GTEEmbeddingModel()


class EmbeddingRequest(BaseModel):
    batch: list[str]

    @field_validator("batch")
    @classmethod
    def batch_not_empty(cls, v):
        if not v:
            raise ValueError("Batch cannot be empty")
        return v


@app.post("/generate_embedding")
async def generate_embedding(request: EmbeddingRequest):
    return model._encode_batch(request.batch).tolist()


@app.get("/")
def root():
    return {"ok": True}


# To run: uvicorn embedding_factory:app --host 0.0.0.0 --port 8000
