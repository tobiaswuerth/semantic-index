import logging
from typing import Iterator
import tqdm

from ..data.models import Source
from ..embeddings import chunk_text
from ..data.repository import EmbeddingRepository, SourceRepository
from ..embeddings.factory import EmbeddingFactory
from ..sources.handler import SourceHandler
from ..sources.resolver import Resolver

logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(
        self,
        source_repo: SourceRepository,
        embedding_repo: EmbeddingRepository,
        embedding_factory: EmbeddingFactory,
        resolver: Resolver,
    ):
        self._source_repo = source_repo
        self._embedding_repo = embedding_repo
        self._embedding_factory = embedding_factory
        self._resolver = resolver

    def ingest_sources(self, sources: Iterator[Source]) -> int:
        logger.info("Ingesting sources...")
        count = self._source_repo.upsert_many(sources)
        logger.info(f"Ingested {count} sources")
        return count

    def process_pending_sources(
        self,
        sources: list[Source],
        *,
        show_progress: bool = True,
    ) -> tuple[int, int]:
        logger.info("Processing sources...")

        todo = [
            s
            for s in sources
            if not s.error
            and (not s.last_processed or s.last_modified > s.last_processed)
        ]
        logger.info(f"Found {len(todo)} sources to process")

        processed_count = 0
        error_count = 0

        iterator = (
            tqdm.tqdm(todo, desc="Processing", unit="source") if show_progress else todo
        )

        for source in iterator:
            try:
                self._process_single_source(source)
                processed_count += 1
            except Exception as e:
                error_count += 1
                source.error = True
                source.error_message = str(e)
                self._source_repo.update(source)
                logger.error(f"Error processing {source.uri}: {e}")

        logger.info(
            f"Finished processing: {processed_count} success, {error_count} errors"
        )
        return processed_count, error_count

    def _process_single_source(self, source: Source) -> None:
        self._embedding_repo.delete_by_source_id(source.id)

        handler: SourceHandler = self._resolver.find_for(source)
        contents = handler.read(source)

        if not contents or not contents.strip():
            raise ValueError(f"Source {source.uri} is empty")

        embeddings = self._embedding_factory.process(contents, source)
        self._embedding_repo.create_many(embeddings)

        source.last_processed = source.last_modified
        self._source_repo.update(source)

    def read_chunk_content(self, source: Source, chunk_idx: int) -> str:
        handler = self._resolver.find_for(source)
        content = handler.read(source)
        chunks = chunk_text(content)

        if chunk_idx < 0 or chunk_idx >= len(chunks):
            raise IndexError(f"Chunk index {chunk_idx} out of range")

        return chunks[chunk_idx].text
