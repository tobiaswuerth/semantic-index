from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from typing import Callable, List

from .manager import Manager, get_manager
from .dto import (
    SourceSchema,
    EmbeddingSchema,
    SearchRequest,
    SearchResponse,
    ReadContentResult,
    HistogramResponse,
    TagCount,
)


router = APIRouter(prefix="/api")


@router.get("/", response_model=dict)
def root():
    return {"ok": True}


def _search_with_date_filter(
    request: SearchRequest,
    target_fn: Callable[[SearchRequest], list[SearchResponse]],
) -> list[SearchResponse]:
    results = target_fn(request)
    return [
        SearchResponse(
            source=SourceSchema.model_validate(r.source),
            embedding=EmbeddingSchema.model_validate(r.embedding),
            similarity=r.similarity,
        )
        for r in results
    ]


@router.post("/search/chunks", response_model=list[SearchResponse])
async def search_knn_chunks_by_query(
    request: SearchRequest,
    manager: Manager = Depends(get_manager),
) -> list[SearchResponse]:
    return await run_in_threadpool(
        _search_with_date_filter,
        request,
        manager.search_service.search_chunks,
    )


@router.post("/search/docs", response_model=list[SearchResponse])
async def search_knn_docs_by_query(
    request: SearchRequest,
    manager: Manager = Depends(get_manager),
) -> list[SearchResponse]:
    return await run_in_threadpool(
        _search_with_date_filter,
        request,
        manager.search_service.search_documents,
    )


@router.get("/embedding/{id_}/content", response_model=ReadContentResult)
async def read_content_by_embedding_id(
    id_: int,
    manager: Manager = Depends(get_manager),
) -> ReadContentResult:
    if id_ < 0:
        raise HTTPException(status_code=400, detail="Invalid embedding ID")

    emb = await run_in_threadpool(manager.repo_embedding.get_by_id, id_)
    if emb is None:
        raise KeyError(f"Embedding {id_} not found")

    source = await run_in_threadpool(manager.repo_source.get_by_id, emb.source_id)
    if source is None:
        raise KeyError(f"Source for embedding {id_} not found")

    content = await run_in_threadpool(
        manager.processing_service.read_chunk_content, source, emb.chunk_idx
    )
    return ReadContentResult(section=content)


@router.get("/source/histogram/createdate", response_model=list[HistogramResponse])
async def get_createdate_histogram(
    manager: Manager = Depends(get_manager),
) -> list[HistogramResponse]:
    return await run_in_threadpool(manager.repo_source.get_createdate_histogram)


@router.get("/source/histogram/modifydate", response_model=list[HistogramResponse])
async def get_modifydate_histogram(
    manager: Manager = Depends(get_manager),
) -> list[HistogramResponse]:
    return await run_in_threadpool(manager.repo_source.get_modifydate_histogram)


@router.get("/tags", response_model=List[TagCount])
async def get_tags(
    manager: Manager = Depends(get_manager),
) -> List[TagCount]:
    data = await run_in_threadpool(manager.repo_tag.get_counted)
    return data
