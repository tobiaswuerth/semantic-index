import logging

from ..data import (
    init_db,
    EmbeddingRepository,
    SourceHandlerRepository,
    SourceRepository,
    SourceTypeRepository,
)
from ..embeddings import EmbeddingFactory
from ..services import ProcessingService, SearchService
from ..sources import Resolver, FileSourceHandler, JiraSourceHandler


class Manager:
    def __init__(self):
        global _manager
        assert _manager is None, "Manager instance already exists! use get_manager()"
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Semantic Index Manager...")

        init_db()
        self.repo_source_handler = SourceHandlerRepository()
        self.repo_source_type = SourceTypeRepository()
        self.repo_source = SourceRepository()
        self.repo_embedding = EmbeddingRepository()
        self.resolver = Resolver(
            handler_repo=self.repo_source_handler,
            type_repo=self.repo_source_type,
        )
        self.resolver.register(FileSourceHandler())
        self.resolver.register(JiraSourceHandler())

        self.embedding_factory = EmbeddingFactory()
        self._processing_service = None
        self._search_service = None

        self.logger.info("Semantic Index Manager initialized.")

    @property
    def processing_service(self) -> ProcessingService:
        if self._processing_service is None:
            self._processing_service = ProcessingService(
                source_repo=self.repo_source,
                embedding_repo=self.repo_embedding,
                embedding_factory=self.embedding_factory,
                resolver=self.resolver,
            )
        return self._processing_service

    @property
    def search_service(self) -> SearchService:
        if self._search_service is None:
            self._search_service = SearchService(
                embedding_repo=self.repo_embedding,
                source_repo=self.repo_source,
                embedding_factory=self.embedding_factory,
            )
        return self._search_service


_manager: Manager = None  # type: ignore


def get_manager() -> Manager:
    global _manager
    if _manager is None:
        _manager = Manager()
    return _manager
