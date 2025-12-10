import logging
from typing import Iterator

from .api.schemas import ContentSchema, SearchResultSchema, SourceSchema
from .data import EmbeddingRepository, SourceRepository, init_db
from .data.models import Source
from .embeddings import EmbeddingFactory
from .services import ProcessingService, SearchService
from .sources import FileSourceHandler, Resolver


class Manager:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        init_db()

        self._source_repo = SourceRepository()
        self._embedding_repo = EmbeddingRepository()
        self._embedding_factory = EmbeddingFactory()

        self._resolver = Resolver()
        self._resolver.register(FileSourceHandler())

        self._processing_service = ProcessingService(
            source_repo=self._source_repo,
            embedding_repo=self._embedding_repo,
            embedding_factory=self._embedding_factory,
            resolver=self._resolver,
        )

        self._load_data()

    def _load_data(self) -> None:
        self._logger.info("Loading data from database...")
        self._sources = self._source_repo.get_all(order_by_modified=True)
        self._source_by_id = {s.id: s for s in self._sources}
        self._embeddings = self._embedding_repo.get_all()

        self._search_service = SearchService(
            model=self._embedding_factory.model,
            embeddings=self._embeddings,
            source_lookup=self._source_by_id,
        )
        self._logger.info(
            f"Loaded {len(self._sources)} sources, {len(self._embeddings)} embeddings"
        )

    @property
    def sources(self) -> list[Source]:
        return self._sources

    @property
    def embedding_factory(self) -> EmbeddingFactory:
        return self._embedding_factory

    def process_sources(self) -> None:
        self._processing_service.process_pending_sources(self._sources)
        self._load_data()

    def ingest_sources(self, sources: Iterator[Source]) -> int:
        count = self._processing_service.ingest_sources(sources)
        self._load_data()
        return count

    def find_knn_chunks(self, query: str, k: int = 10) -> list[SearchResultSchema]:
        results = self._search_service.search_chunks(query, k)
        return [
            SearchResultSchema(
                source=SourceSchema.model_validate(r.source),
                similarity=r.similarity,
                embedding_id=r.embedding.id,
            )
            for r in results
        ]

    def find_knn_docs(self, query: str, k: int = 10) -> list[SearchResultSchema]:
        results = self._search_service.search_documents(query, k)
        return [
            SearchResultSchema(
                source=SourceSchema.model_validate(r.source),
                similarity=r.similarity,
                embedding_id=r.embedding.id,
            )
            for r in results
        ]

    def read_content_by_embedding_id(self, embedding_id: int) -> ContentSchema:
        emb = self._embedding_repo.get_by_id(embedding_id)
        if emb is None:
            raise KeyError(f"Embedding {embedding_id} not found")

        source = self._source_by_id.get(emb.source_id)
        if source is None:
            raise KeyError(f"Source for embedding {embedding_id} not found")

        content = self._processing_service.read_chunk_content(source, emb.chunk_idx)
        return ContentSchema(section=content)
