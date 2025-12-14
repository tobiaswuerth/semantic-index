import logging
import os
from datetime import datetime
from typing import Iterator

from ..data import Source
from .io import get_file_extension, supported_extensions, extension_to_reader
from .base_handler import BaseSourceHandler

logger = logging.getLogger(__name__)


class FileSourceHandler(BaseSourceHandler):
    def get_name(self) -> str:
        return "File"

    def index_all(self, base: str) -> Iterator[Source]:
        if not os.path.isdir(base):
            raise ValueError(f"Base path is not a directory: {base}")

        for root, _, files in os.walk(base):
            for file in files:
                path = os.path.join(root, file)
                yield self.index_one(path)

    def index_one(self, uri: str) -> Source:
        if not os.path.isfile(uri):
            raise ValueError(f"Source path is not a file: {uri}")

        stat = os.stat(uri)
        obj_created = datetime.fromtimestamp(stat.st_birthtime)
        obj_modified = datetime.fromtimestamp(stat.st_mtime)
        if obj_created > obj_modified:
            logger.warning(
                (
                    f"File modification time is earlier than creation time for {uri}. "
                    f"Setting modification time to creation time."
                    f"{obj_created=} > {obj_modified=}"
                )
            )
            obj_modified = obj_created

        ext = get_file_extension(uri)
        tags = [self.handler_tag, self.repo_tag.get_or_create(ext)]

        logger.debug(f"Indexing file: {uri}")
        return Source(
            id=None,
            source_handler_id=self.handler.id,
            uri=uri,
            resolved_to=f"file://{uri}",
            title=os.path.basename(uri),
            obj_created=obj_created,
            obj_modified=obj_modified,
            last_checked=datetime.now(),
            last_processed=None,
            error=False,
            error_message=None,
            tags=tags,
        )

    def _read_source(self, source: Source) -> str:
        ext = get_file_extension(source.uri)
        if ext not in supported_extensions:
            raise ValueError(f"Unsupported file extension: {ext}")

        reader = extension_to_reader[ext]
        return reader(source.uri)
