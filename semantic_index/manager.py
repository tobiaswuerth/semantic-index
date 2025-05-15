import logging

from .embeddings import EmbeddingFactory
from .index import Index
from .sources import Resolver, SourceHandler


class Manager:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.index: Index = Index()
        self.embedding_factory: EmbeddingFactory = EmbeddingFactory()
        self.resolver: Resolver = Resolver()

    def process_sources(self):
        for source in self.index.sources:
            if source.last_processed and source.last_modified <= source.last_processed:
                continue

            # source has changed, update embeddings
            self.logger.info(f"Processing source: {source.uri}...")
            self.index.delete_embeddings(source)

            handler: SourceHandler = self.resolver.find_for(source)
            contents = handler.read(source)
            if contents is None:
                continue

            embeddings = self.embedding_factory.process(contents, source)
            self.index.create_embeddings(embeddings)
            source.last_processed = source.last_modified
            self.index.update_source(source)

            self.index.reload_data()

            # finalize
            self.logger.info(f"Processed source: {source.uri}")
