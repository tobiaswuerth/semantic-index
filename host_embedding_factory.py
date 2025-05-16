from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback

from semantic_index import GTEEmbeddingModel

embedding_model: GTEEmbeddingModel = GTEEmbeddingModel()
app = FastAPI()


class EmbeddingRequest(BaseModel):
    batch: list[str]


@app.post("/generate_embedding")
async def generate_embedding(request: EmbeddingRequest):
    try:
        if not request.batch:
            raise HTTPException(status_code=400, detail="Missing 'batch' field in JSON")
        embeddings = embedding_model._encode_batch(request.batch)
        return JSONResponse(content=embeddings.tolist())
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


# To run: uvicorn host_embedding_factory:app --host 0.0.0.0 --port 8000
