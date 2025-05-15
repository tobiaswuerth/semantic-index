import os
import logging
import numpy as np
import sqlite3
from typing import Generator

from .models import Embedding, Source
from .config import config


class Index:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.sources: list[Source] = []
        self.embeddings: list[Embedding] = []

        self._initialize_db()

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
                        last_processed TIMESTAMP
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

    def load(self):
        self.logger.info("Loading database...")
        with self._get_connection() as conn:
            cursor = conn.cursor()

            self.logger.info("Loading database sources...")
            cursor.execute("SELECT id, uri, last_modified, last_processed FROM sources")
            self.sources = []
            for row in cursor.fetchall():
                self.sources.append(
                    Source(
                        id=row[0],
                        uri=row[1],
                        last_modified=row[2],
                        last_processed=row[3],
                    )
                )

            self.logger.info("Loading database embeddings...")
            cursor.execute(
                "SELECT id, source_id, embedding, section_from, section_to FROM embeddings"
            )
            self.embeddings = []
            for row in cursor.fetchall():
                embedding = np.frombuffer(row[2], dtype=np.float32)
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

            for source in sources:
                cursor.execute(
                    """ INSERT INTO sources (uri, last_modified, last_processed)
                        VALUES (?, ?, ?)
                        ON CONFLICT(uri) DO UPDATE SET
                            last_modified = ?
                    """,
                    (
                        source.uri,
                        source.last_modified,
                        source.last_processed,
                        source.last_modified,
                    ),
                )
                conn.commit()
                self.logger.debug(f"Inserted source: {source.uri}")

        # reload data
        self.load()
