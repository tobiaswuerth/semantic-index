import logging
import numpy as np

from ..data import Embedding, EmbeddingRepository, SourceRepository
from ..embeddings import get_similarities, EmbeddingFactory
from ..api import SearchResponse, SearchRequest


logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
        self,
        embedding_repo: EmbeddingRepository,
        source_repo: SourceRepository,
        embedding_factory: EmbeddingFactory,
    ):
        self._embedding_repo = embedding_repo
        self._source_repo = source_repo
        self._embedding_factory = embedding_factory

    def _get_similar_embeddings(
        self, request: SearchRequest
    ) -> tuple[list[Embedding], np.ndarray, np.ndarray]:
        embeddings = self._embedding_repo.get_all_with_date_and_type(
            request.date_filter, request.source_type_ids
        )
        if not embeddings:
            return [], np.array([]), np.array([])

        query_emb = self._embedding_factory.model.encode([request.query])[0]
        emb_matrix = np.vstack([e.embedding for e in embeddings])
        similarities, indices = get_similarities(query_emb, emb_matrix)
        return embeddings, similarities, indices

    def search_chunks(self, request: SearchRequest) -> list[SearchResponse]:
        embeddings, similarities, indices = self._get_similar_embeddings(request)
        if not embeddings:
            return []

        results: list[SearchResponse] = []
        top_indices: list[int] = indices[: request.limit].tolist()
        for idx in top_indices:
            emb = embeddings[idx]
            source = self._source_repo.get_by_id(emb.source_id)
            assert source
            results.append(
                SearchResponse(
                    source=source,
                    embedding=emb,
                    similarity=float(similarities[idx]),
                )
            )
        return results

    def search_documents(self, request: SearchRequest) -> list[SearchResponse]:
        embeddings, similarities, indices = self._get_similar_embeddings(request)
        if not embeddings:
            return []

        seen_sources: set[int] = set()
        results: list[SearchResponse] = []
        all_indices: list[int] = indices.tolist()
        for idx in all_indices:
            if len(results) >= request.limit:
                break

            emb = embeddings[idx]
            if emb.source_id in seen_sources:
                continue

            source = self._source_repo.get_by_id(emb.source_id)
            assert source

            seen_sources.add(emb.source_id)
            results.append(
                SearchResponse(
                    source=source,
                    embedding=emb,
                    similarity=float(similarities[idx]),
                )
            )
        return results
