import logging
from dataclasses import dataclass
import numpy as np

from ..data import Embedding, Source, EmbeddingRepository, SourceRepository
from ..embeddings import get_similarities, EmbeddingFactory

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SearchResult:
    source: Source
    embedding: Embedding
    similarity: float


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

    def search_chunks(self, query: str, k: int = 10) -> list[SearchResult]:
        embeddings = self._embedding_repo.get_all()
        if not embeddings:
            return []

        query_emb = self._embedding_factory.model.encode([query])[0]
        emb_matrix = np.vstack([e.embedding for e in embeddings])
        similarities, indices = get_similarities(query_emb, emb_matrix)

        results: list[SearchResult] = []
        top_indices: list[int] = indices[:k].tolist()
        for idx in top_indices:
            emb = embeddings[idx]
            source = self._source_repo.get_by_id(emb.source_id)
            if source:
                results.append(
                    SearchResult(
                        source=source,
                        embedding=emb,
                        similarity=float(similarities[idx]),
                    )
                )
        return results

    def search_documents(self, query: str, k: int = 10) -> list[SearchResult]:
        embeddings = self._embedding_repo.get_all()
        if not embeddings:
            return []

        query_emb = self._embedding_factory.model.encode([query])[0]
        emb_matrix = np.vstack([e.embedding for e in embeddings])
        similarities, indices = get_similarities(query_emb, emb_matrix)

        seen_sources: set[int] = set()
        results: list[SearchResult] = []
        all_indices: list[int] = indices.tolist()
        for idx in all_indices:
            if len(results) >= k:
                break
            emb = embeddings[idx]
            if emb.source_id not in seen_sources:
                source = self._source_repo.get_by_id(emb.source_id)
                if source:
                    seen_sources.add(emb.source_id)
                    results.append(
                        SearchResult(
                            source=source,
                            embedding=emb,
                            similarity=float(similarities[idx]),
                        )
                    )
        return results
