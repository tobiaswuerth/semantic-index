from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import json

from semantic_index import Manager, exception_handled_json_api

manager: Manager = Manager()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchKnnByQueryRequest(BaseModel):
    query: str
    limit: int = Field(default=5, ge=1, le=100)

    @field_validator("query")
    def query_not_empty(cls, v):
        if not v:
            raise ValueError("Query cannot be empty")
        return v


@app.post("/api/search_knn_by_query")
@exception_handled_json_api
async def search_knn_by_query(request: SearchKnnByQueryRequest):
    return manager.find_knn(request.query, request.limit)


# To run: uvicorn backend:app --host 0.0.0.0 --port 5000
