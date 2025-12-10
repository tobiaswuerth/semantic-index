import logging
from dataclasses import dataclass
import numpy as np

from ..data import Embedding, Source
from ..embeddings.model import BaseEmbeddingModel
from ..embeddings.utils import get_similarities

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SearchResult:
    source: Source
    embedding: Embedding
    similarity: float


class SearchService:
    def __init__(
        self,
        model: BaseEmbeddingModel,
        embeddings: list[Embedding],
        source_lookup: dict[int, Source],
    ):
        self._model = model
        self._embeddings = embeddings
        self._source_lookup = source_lookup
        self._embedding_matrix: np.ndarray | None = None

    def _get_embedding_matrix(self) -> np.ndarray:
        if self._embedding_matrix is None and self._embeddings:
            self._embedding_matrix = np.vstack([e.embedding for e in self._embeddings])
        return (
            self._embedding_matrix
            if self._embedding_matrix is not None
            else np.array([])
        )

    def search_chunks(self, query: str, k: int = 10) -> list[SearchResult]:
        if not self._embeddings:
            return []

        query_emb = self._model.encode([query])[0]
        emb_matrix = self._get_embedding_matrix()
        similarities, indices = get_similarities(query_emb, emb_matrix)

        results: list[SearchResult] = []
        top_indices: list[int] = indices[:k].tolist()
        for idx in top_indices:
            emb = self._embeddings[idx]
            source = self._source_lookup.get(emb.source_id)
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
        if not self._embeddings:
            return []

        query_emb = self._model.encode([query])[0]
        emb_matrix = self._get_embedding_matrix()
        similarities, indices = get_similarities(query_emb, emb_matrix)

        seen_sources: set[int] = set()
        results: list[SearchResult] = []
        all_indices: list[int] = indices.tolist()
        for idx in all_indices:
            if len(results) >= k:
                break
            emb = self._embeddings[idx]
            if emb.source_id not in seen_sources:
                source = self._source_lookup.get(emb.source_id)
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
