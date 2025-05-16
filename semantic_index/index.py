import os
import logging
import numpy as np
import sqlite3
from typing import Generator, List

from .models import Embedding, Source
from .config import config


class Index:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.sources: list[Source] = []
        self.embeddings: list[Embedding] = []
        self._initialize_db()
        self.reload_data()

    def _initialize_db(self):
        if os.path.exists(config.index_path):
            return

        self.logger.info(f"Creating index database at {config.index_path}...")
        if os.path.dirname(config.index_path):
            os.makedirs(os.path.dirname(config.index_path), exist_ok=True)

        with sqlite3.connect(
            config.index_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """ CREATE TABLE IF NOT EXISTS sources (
                        id INTEGER PRIMARY KEY,
                        uri TEXT NOT NULL UNIQUE,
                        last_modified TIMESTAMP NOT NULL,
                        last_processed TIMESTAMP,
                        error BOOLEAN,
                        error_message TEXT
                    )"""
            )

            cursor.execute(
                """ CREATE TABLE IF NOT EXISTS embeddings (
                        id INTEGER PRIMARY KEY,
                        source_id INTEGER NOT NULL,
                        embedding BLOB NOT NULL,
                        section_from INTEGER NOT NULL,
                        section_to INTEGER NOT NULL,
                        FOREIGN KEY (source_id) REFERENCES sources (id)
                    )"""
            )

            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_embeddings_source_id ON embeddings (source_id)"
            )
            conn.commit()

        self.logger.info("Database initialized")

    def _get_connection(self):
        return sqlite3.connect(config.index_path, detect_types=sqlite3.PARSE_DECLTYPES)

    def reload_data(self):
        self.logger.info("Loading database...")
        with self._get_connection() as conn:
            cursor = conn.cursor()

            self.logger.info("Loading database sources...")
            cursor.execute("SELECT id, uri, last_modified, last_processed, error, error_message FROM sources ORDER BY last_modified DESC")
            self.sources = []
            for row in cursor.fetchall():
                self.sources.append(
                    Source(
                        id=row[0],
                        uri=row[1],
                        last_modified=row[2],
                        last_processed=row[3],
                        error=row[4],
                        error_message=row[5],
                    )
                )

            self.logger.info("Loading database embeddings...")
            cursor.execute(
                "SELECT id, source_id, embedding, section_from, section_to FROM embeddings"
            )
            self.embeddings = []
            for row in cursor.fetchall():
                embedding = np.frombuffer(row[2], dtype=np.float16)
                self.embeddings.append(
                    Embedding(
                        id=row[0],
                        source_id=row[1],
                        embedding=embedding,
                        section_from=row[3],
                        section_to=row[4],
                    )
                )

        self.logger.info(
            f"Loaded {len(self.sources)} sources and {len(self.embeddings)} embeddings from the database"
        )

    def ingest_sources(self, sources: Generator[Source, None, None]):
        self.logger.info("Ingesting sources into the database...")
        with self._get_connection() as conn:
            cursor = conn.cursor()

            si = 0
            for si, source in enumerate(sources):
                cursor.execute(
                    """ INSERT INTO sources (uri, last_modified, last_processed, error, error_message)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(uri) DO UPDATE SET
                            last_modified = ?
                    """,
                    (
                        source.uri,
                        source.last_modified,
                        source.last_processed,
                        source.error,
                        source.error_message,
                        source.last_modified,

                    ),
                )
                if (si + 1) % 1000 == 0:
                    conn.commit()
                    self.logger.debug(f"Inserted {si + 1} sources into the database...")
            conn.commit()
        self.logger.info(f"Inserted {si} sources into the database")

    def create_embeddings(self, embeddings: List[Embedding]):
        self.logger.debug("Creating embeddings in the database...")
        with self._get_connection() as conn:
            cursor = conn.cursor()

            for embedding in embeddings:
                cursor.execute(
                    """ INSERT INTO embeddings (source_id, embedding, section_from, section_to)
                        VALUES (?, ?, ?, ?)
                    """,
                    (
                        embedding.source_id,
                        embedding.embedding.astype(np.float16).tobytes(),
                        embedding.section_from,
                        embedding.section_to,
                    ),
                )
            conn.commit()
        self.logger.debug(f"Inserted {len(embeddings)} embeddings into the database")

    def delete_embeddings(self, source: Source):
        assert source.id is not None, "Source ID must be set"
        self.logger.debug(f"Deleting embeddings for source ID: {source.id}")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM embeddings WHERE source_id = ?",
                (source.id,),
            )
            conn.commit()
        self.logger.debug(f"Deleted embeddings for source ID: {source.id}")

    def update_source(self, source: Source):
        assert source.id is not None, "Source ID must be set"
        self.logger.debug(f"Updating source ID: {source.id}")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """ UPDATE sources
                    SET last_processed = ?, 
                        error = ?,
                        error_message = ?
                    WHERE id = ?
                """,
                (source.last_processed, source.error, source.error_message, source.id),
            )
            conn.commit()
        self.logger.debug(f"Updated source ID: {source.id}")
