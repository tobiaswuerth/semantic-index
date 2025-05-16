import logging
import numpy as np
import tqdm

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
        self.logger.info("Processing sources...")
        todo = [
            source
            for source in self.index.sources
            if not source.error
            and (
                not source.last_processed
                or source.last_modified > source.last_processed
            )
        ]

        logging.info(f"Found {len(todo)} sources to process.")

        for source in tqdm.tqdm(todo, desc="Processing sources", unit="source"):
            self.index.delete_embeddings(source)

            handler: SourceHandler = self.resolver.find_for(source)
            try:
                contents = handler.read(source)
                if contents is None or not contents.strip():
                    raise ValueError(f"Source {source.uri} is empty or not readable.")
            except Exception as e:
                source.error = True
                source.error_message = str(e)
                self.index.update_source(source)
                self.logger.error(f"Error processing source {source.uri}: {e}")
                continue

            embeddings = self.embedding_factory.process(contents, source)
            self.index.create_embeddings(embeddings)
            source.last_processed = source.last_modified
            self.index.update_source(source)

        self.logger.info("Finished processing sources.")
        self.index.reload_data()

    def find_knn(self, query: str, k: int = 5):
        self.logger.info(f"Finding {k} nearest neighbors for query: {query}")

        # get embeddings
        query_embedding = self.embedding_factory.model.encode([query])[0]
        all_embeddings = np.vstack([e.embedding for e in self.index.embeddings])

        # Cosine similarity calculation (normalized dot product)
        similarities = np.dot(all_embeddings, query_embedding)
        norms = np.linalg.norm(all_embeddings, axis=1) * np.linalg.norm(query_embedding)
        similarities = similarities / norms
        top_indices = np.argsort(similarities)[-k:][::-1]

        # Print the top k results
        source_map = {src.id: src for src in self.index.sources}
        for idx in top_indices:
            embedding = self.index.embeddings[idx]
            source = source_map[embedding.source_id]
            print(f"Source: {source.uri}")
            print(f"Similarity: {similarities[idx]:.4f}")
            print()
