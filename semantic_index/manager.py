import logging
import numpy as np
import tqdm
from sklearn.neighbors import NearestNeighbors
from fastapi import HTTPException

from .embeddings import EmbeddingFactory
from .index import Index
from .sources import Resolver, SourceHandler, FileSourceHandler
from .models import Embedding, Source


class Manager:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.index: Index = Index()
        self.embedding_factory: EmbeddingFactory = EmbeddingFactory()

        self.resolver: Resolver = Resolver()
        self.resolver.register(FileSourceHandler())

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
            self.index.delete_embeddings_by_source(source)

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

    def find_knn(self, query: str, k: int = 10):
        self.logger.info(f"Finding {k} nearest neighbors for query: {query}")

        print("Finding nearest neighbors...")
        # get embeddings
        query_embedding = self.embedding_factory.model.encode([query])[0]
        all_embeddings = np.vstack([e.embedding for e in self.index.embeddings])

        print("Using sklearn KNN to find neighbors...")
        knn = NearestNeighbors(n_neighbors=k, metric="cosine")
        knn.fit(all_embeddings)
        distances, indices = knn.kneighbors([query_embedding], n_neighbors=k)
        similarities = 1 - distances[0]

        print("Top k results...")
        results = []
        for i, idx in enumerate(indices[0]):
            embedding: Embedding = self.index.embeddings[idx]
            source = self.index.source_by_id[embedding.source_id]

            results.append(
                {
                    "source": source.to_dict(),
                    "similarity": float(similarities[i]),
                    "embedding_id": embedding.id,
                }
            )

        print("done")
        return results

    def read_content_by_embedding_id(self, embedding_id: int) -> dict:
        self.logger.info(f"Reading content for embedding ID: {embedding_id}")
        embedding: Embedding | None = self.index.get_embedding_by_id(embedding_id)
        if embedding is None:
            raise HTTPException(status_code=404, detail="Embedding not found")
        source: Source = self.index.source_by_id[embedding.source_id]

        handler: SourceHandler = self.resolver.find_for(source)
        content = handler.read(source)
        return {
            "section": content[embedding.section_from : embedding.section_to],
        }
