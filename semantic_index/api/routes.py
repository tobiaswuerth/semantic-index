from fastapi import APIRouter, Depends, HTTPException

from ..manager import Manager
from .dependencies import get_manager
from .schemas import ContentSchema, SearchQueryRequest, SearchResultSchema

router = APIRouter(prefix="/api")


@router.post(
    "/search_knn_chunks_by_query",
    response_model=list[SearchResultSchema],
)
async def search_knn_chunks_by_query(
    request: SearchQueryRequest,
    manager: Manager = Depends(get_manager),
) -> list[SearchResultSchema]:
    return manager.find_knn_chunks(request.query, request.limit)


@router.post(
    "/search_knn_docs_by_query",
    response_model=list[SearchResultSchema],
)
async def search_knn_docs_by_query(
    request: SearchQueryRequest,
    manager: Manager = Depends(get_manager),
) -> list[SearchResultSchema]:
    return manager.find_knn_docs(request.query, request.limit)


@router.get(
    "/read_content_by_embedding_id/{embedding_id}",
    response_model=ContentSchema,
)
async def read_content_by_embedding_id(
    embedding_id: int,
    manager: Manager = Depends(get_manager),
) -> ContentSchema:
    if embedding_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid embedding ID")
    try:
        return manager.read_content_by_embedding_id(embedding_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
