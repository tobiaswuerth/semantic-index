import logging
import os
from datetime import datetime
from typing import Iterator

from ..data import Source
from .io import supported_extensions, extension_to_reader
from .base_handler import BaseSourceHandler

logger = logging.getLogger(__name__)


class FileSourceHandler(BaseSourceHandler):
    handler_name = "File"
    source_types = {
        "Text": [".txt", ".md"],
        "Data": [".csv", ".sql", ".json", ".xml"],
        "System": [".yaml", ".ini", ".log"],
        "Word": [".docx"],
        "PDF": [".pdf"],
        "Mail": [".msg"],
    }

    def __init__(self):
        super().__init__()
        self.ext_to_name = {
            ext: type_name
            for type_name, ext_list in self.source_types.items()
            for ext in ext_list
        }

    def index_all(self, base: str) -> Iterator[Source]:
        if not os.path.isdir(base):
            raise ValueError(f"Base path is not a directory: {base}")

        for root, _, files in os.walk(base):
            for file in files:
                path = os.path.join(root, file)
                try:
                    yield self.index_one(path)
                except Exception as e:
                    logger.warning(f"Failed to index file {path}: {e}")

    def index_one(self, uri: str) -> Source:
        if not os.path.isfile(uri):
            raise ValueError(f"Source path is not a file: {uri}")

        ext = os.path.splitext(uri)[1].lower()
        if ext not in self.ext_to_name:
            raise ValueError(f"Unsupported file extension: {ext}")

        type_name = self.ext_to_name[ext]
        type_model = self.source_type_by_name(type_name)
        assert type_model
        handler_model = self.get_handler()
        assert handler_model

        stat = os.stat(uri)
        obj_created = datetime.fromtimestamp(stat.st_birthtime)
        obj_modified = datetime.fromtimestamp(stat.st_mtime)

        logger.debug(f"Indexing file: {uri}")
        return Source(
            id=None,
            source_handler_id=handler_model.id,
            source_type_id=type_model.id,
            uri=uri,
            resolved_to=f"file://{uri}",
            title=os.path.basename(uri),
            obj_created=obj_created,
            obj_modified=obj_modified,
            last_checked=datetime.now(),
            last_processed=None,
            error=False,
            error_message=None,
        )

    def _read_source(self, source: Source) -> str:
        ext = os.path.splitext(source.uri)[1].lower()
        if ext not in supported_extensions:
            raise ValueError(f"Unsupported file extension: {ext}")

        reader = extension_to_reader[ext]
        return reader(source.uri)
