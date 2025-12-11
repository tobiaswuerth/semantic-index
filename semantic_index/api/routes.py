from fastapi import APIRouter, Depends, HTTPException

from .manager import Manager, get_manager
from .schemas import ContentSchema, SearchQueryRequest, SearchResultSchema, SourceSchema

router = APIRouter(prefix="/api")


@router.post(
    "/search_knn_chunks_by_query",
    response_model=list[SearchResultSchema],
)
async def search_knn_chunks_by_query(
    request: SearchQueryRequest,
    manager: Manager = Depends(get_manager),
) -> list[SearchResultSchema]:
    results = manager.search_service.search_chunks(request.query, request.limit)
    return [
        SearchResultSchema(
            source=SourceSchema.model_validate(r.source),
            similarity=r.similarity,
            embedding_id=r.embedding.id,
        )
        for r in results
    ]


@router.post(
    "/search_knn_docs_by_query",
    response_model=list[SearchResultSchema],
)
async def search_knn_docs_by_query(
    request: SearchQueryRequest,
    manager: Manager = Depends(get_manager),
) -> list[SearchResultSchema]:
    results = manager.search_service.search_documents(request.query, request.limit)
    return [
        SearchResultSchema(
            source=SourceSchema.model_validate(r.source),
            similarity=r.similarity,
            embedding_id=r.embedding.id,
        )
        for r in results
    ]


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

    emb = manager.repo_embedding.get_by_id(embedding_id)
    if emb is None:
        raise KeyError(f"Embedding {embedding_id} not found")

    source = manager.repo_source.get_by_id(emb.source_id)
    if source is None:
        raise KeyError(f"Source for embedding {embedding_id} not found")

    content = manager.processing_service.read_chunk_content(source, emb.chunk_idx)
    return ContentSchema(section=content)
