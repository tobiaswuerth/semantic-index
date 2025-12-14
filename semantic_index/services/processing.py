import logging
from typing import Iterator
from tqdm import tqdm
import traceback
from datetime import datetime

from ..data import Source, EmbeddingRepository, SourceRepository
from ..embeddings import chunk_text, EmbeddingFactory
from ..sources import BaseSourceHandler, Handler


logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(
        self,
        source_repo: SourceRepository,
        embedding_repo: EmbeddingRepository,
        embedding_factory: EmbeddingFactory,
        handler: Handler,
    ):
        self._source_repo = source_repo
        self._embedding_repo = embedding_repo
        self._embedding_factory = embedding_factory
        self._handler = handler

    def ingest_sources(self, sources: Iterator[Source]) -> None:
        logger.info("Ingesting sources...")
        try:
            batch_size = 100
            updated, inserted = 0, 0

            def _handle_batch():
                nonlocal updated, inserted
                updated_batch, inserted_batch = self._source_repo.upsert_many(batch)
                updated += updated_batch
                inserted += inserted_batch
                batch.clear()

            batch: list[Source] = []
            for source in tqdm(sources, desc="Ingesting", unit=" Sources"):
                batch.append(source)
                if len(batch) >= batch_size:
                    _handle_batch()
            if batch:
                _handle_batch()
        except KeyboardInterrupt:
            logger.warning("Ingestion operation interrupted by user.")
        logger.info("Ingestion complete.")

    def process_pending_sources(self) -> None:
        logger.info("Processing sources...")
        sources = self._source_repo.get_all()
        if not sources:
            logger.info("No sources to process")
            return

        todo = [
            s
            for s in sources
            if not s.error
            and (not s.last_processed or s.obj_modified > s.last_processed)
        ]
        skipped = len(sources) - len(todo)
        logger.info(f"{skipped} sources skipped, {len(todo)} sources to process.")
        if not todo:
            logger.info("Processing complete.")
            return

        ok, error = 0, 0
        for source in tqdm(todo, desc="Processing", unit=" Sources"):
            try:
                self.process_single_source(source)
                ok += 1
            except Exception as e:
                error += 1
                source.error = True
                source.error_message = str(e)
                self._source_repo.update(source)
                stacktrace = traceback.format_exc()
                logger.error(f"Error processing {source.uri}: {e}\n{stacktrace}")

        logger.info(f"{ok} ok, {error} errors occurred.")
        logger.info("Processing complete.")

    def process_single_source(self, source: Source) -> None:
        self._embedding_repo.delete_by_source_id(source.id)

        handler: BaseSourceHandler = self._handler.find_by_id(source.source_handler_id)
        contents = handler.read(source)
        if not contents or not contents.strip():
            raise ValueError(f"Source {source.uri} is empty")

        embeddings = self._embedding_factory.process(contents, source)
        self._embedding_repo.create_many(embeddings)

        now = datetime.now()
        source.last_checked = now
        source.last_processed = now
        source.error = False
        source.error_message = None
        self._source_repo.update(source)

    def read_chunk_content(self, source: Source, chunk_idx: int) -> str:
        handler = self._handler.find_by_id(source.source_handler_id)
        content = handler.read(source)
        chunks = chunk_text(content)

        if chunk_idx < 0 or chunk_idx >= len(chunks):
            raise IndexError(f"Chunk index {chunk_idx} out of range")

        return chunks[chunk_idx].text
