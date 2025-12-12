from fastapi import APIRouter, Depends, HTTPException
from typing import Callable

from .manager import Manager, get_manager
from .dto import (
    SourceSchema,
    EmbeddingSchema,
    SearchRequest,
    SearchDateFilter,
    SearchResponse,
    ReadContentResult,
)


router = APIRouter(prefix="/api")


def _search_with_date_filter(
    request: SearchRequest,
    target_fn: Callable[[str, SearchDateFilter, int], list[SearchResponse]],
) -> list[SearchResponse]:
    results = target_fn(request.query, request.date_filter, request.limit)
    return [
        SearchResponse(
            source=SourceSchema.model_validate(r.source),
            embedding=EmbeddingSchema.model_validate(r.embedding),
            similarity=r.similarity,
        )
        for r in results
    ]


@router.post("/search_knn_chunks_by_query", response_model=list[SearchResponse])
async def search_knn_chunks_by_query(
    request: SearchRequest,
    manager: Manager = Depends(get_manager),
) -> list[SearchResponse]:
    return _search_with_date_filter(request, manager.search_service.search_chunks)


@router.post("/search_knn_docs_by_query", response_model=list[SearchResponse])
async def search_knn_docs_by_query(
    request: SearchRequest,
    manager: Manager = Depends(get_manager),
) -> list[SearchResponse]:
    return _search_with_date_filter(request, manager.search_service.search_documents)


@router.get(
    "/read_content_by_embedding_id/{embedding_id}",
    response_model=ReadContentResult,
)
async def read_content_by_embedding_id(
    embedding_id: int,
    manager: Manager = Depends(get_manager),
) -> ReadContentResult:
    if embedding_id < 0:
        raise HTTPException(status_code=400, detail="Invalid embedding ID")

    emb = manager.repo_embedding.get_by_id(embedding_id)
    if emb is None:
        raise KeyError(f"Embedding {embedding_id} not found")

    source = manager.repo_source.get_by_id(emb.source_id)
    if source is None:
        raise KeyError(f"Source for embedding {embedding_id} not found")

    content = manager.processing_service.read_chunk_content(source, emb.chunk_idx)
    return ReadContentResult(section=content)


@router.get(
    "/get_createdate_histogram",
    response_model=list[tuple[str, int]],
)
async def get_createdate_histogram(
    manager: Manager = Depends(get_manager),
) -> list[tuple[str, int]]:
    return manager.repo_source.get_createdate_histogram()


@router.get(
    "/get_modifydate_histogram",
    response_model=list[tuple[str, int]],
)
async def get_modifydate_histogram(
    manager: Manager = Depends(get_manager),
) -> list[tuple[str, int]]:
    return manager.repo_source.get_modifydate_histogram()
