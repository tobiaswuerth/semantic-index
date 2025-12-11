import logging
from typing import Iterator

from .api import ContentSchema, SearchResultSchema, SourceSchema
from .data import (
    Source,
    EmbeddingRepository,
    SourceHandlerRepository,
    SourceRepository,
    SourceTypeRepository,
    init_db,
)
from .embeddings import EmbeddingFactory
from .services import ProcessingService, SearchService
from .sources import Resolver, BaseSourceHandler, FileSourceHandler, JiraSourceHandler


class Manager:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._embedding_factory = None
        self._processing_service = None
        self._search_service = None

        init_db()
        self._source_repo = SourceRepository()
        self._embedding_repo = EmbeddingRepository()
        self._handler_repo = SourceHandlerRepository()
        self._type_repo = SourceTypeRepository()

        self._resolver = Resolver(
            handler_repo=self._handler_repo,
            type_repo=self._type_repo,
        )
        self._resolver.register(FileSourceHandler())
        self._resolver.register(JiraSourceHandler())

    @property
    def embedding_factory(self) -> EmbeddingFactory:
        if self._embedding_factory is None:
            self._embedding_factory = EmbeddingFactory()
        return self._embedding_factory

    @property
    def processing_service(self) -> ProcessingService:
        if self._processing_service is None:
            self._processing_service = ProcessingService(
                source_repo=self._source_repo,
                embedding_repo=self._embedding_repo,
                embedding_factory=self.embedding_factory,
                resolver=self._resolver,
            )
        return self._processing_service

    @property
    def search_service(self) -> SearchService:
        if self._search_service is None:
            self._search_service = SearchService(
                embedding_repo=self._embedding_repo,
                source_repo=self._source_repo,
                embedding_factory=self.embedding_factory,
            )
        return self._search_service

    def process_sources(self) -> tuple[int, int]:
        sources = self._source_repo.get_all(order_by_modified=True)
        return self.processing_service.process_pending_sources(sources)

    def ingest_sources(self, sources: Iterator[Source]) -> int:
        return self.processing_service.ingest_sources(sources)

    def find_knn_chunks(self, query: str, k: int = 10) -> list[SearchResultSchema]:
        results = self.search_service.search_chunks(query, k)
        return [
            SearchResultSchema(
                source=SourceSchema.model_validate(r.source),
                similarity=r.similarity,
                embedding_id=r.embedding.id,
            )
            for r in results
        ]

    def find_knn_docs(self, query: str, k: int = 10) -> list[SearchResultSchema]:
        results = self.search_service.search_documents(query, k)
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

        source = self._source_repo.get_by_id(emb.source_id)
        if source is None:
            raise KeyError(f"Source for embedding {embedding_id} not found")

        content = self.processing_service.read_chunk_content(source, emb.chunk_idx)
        return ContentSchema(section=content)

    def get_handler(self, name: str) -> "BaseSourceHandler | None":
        return self._resolver.get_handler_by_name(name)
