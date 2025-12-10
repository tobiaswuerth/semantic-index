import logging
import os
from datetime import datetime
from typing import Callable, Iterator
import docx
import extract_msg
import pymupdf

from ..data import Source
from .base_handler import BaseSourceHandler

logger = logging.getLogger(__name__)


class FileSourceHandler(BaseSourceHandler):
    handler_name = "File"
    source_types = {
        "TXT": [".txt"],
        "Markdown": [".md"],
        "CSV": [".csv"],
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
        self.ext_to_reader = {
            ".txt": self._read_plaintext,
            ".md": self._read_plaintext,
            ".csv": self._read_plaintext,
            ".docx": self._read_docx,
            ".pdf": self._read_pdf,
            ".msg": self._read_msg,
        }

    def crawl(self, base: str, **kwargs) -> Iterator[Source]:
        handler_model = self.get_handler_model()
        assert handler_model

        assert os.path.isdir(base), f"Base path is not a directory: {base}"
        for root, _, files in os.walk(base):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in self.ext_to_name:
                    logger.debug(f"Skipping file with unsupported extension: {file}")
                    continue

                type_name = self.ext_to_name[ext]
                type_model = self.get_type_model(type_name)
                assert type_model

                path = os.path.join(root, file)
                stat = os.stat(path)
                obj_created = datetime.fromtimestamp(stat.st_birthtime)
                obj_modified = datetime.fromtimestamp(stat.st_mtime)

                logger.debug(f"Yield file: {path}")
                yield Source(
                    id=None,
                    source_handler_id=handler_model.id,
                    source_type_id=type_model.id,
                    uri=path,
                    resolved_to=None,
                    title=None,
                    obj_created=obj_created,
                    obj_modified=obj_modified,
                    last_processed=None,
                    error=False,
                    error_message=None,
                )

    def _read_source(self, source: Source) -> str:
        ext = os.path.splitext(source.uri)[1].lower()
        assert ext in self.ext_to_reader
        reader = self.ext_to_reader[ext]
        return reader(source.uri)

    @staticmethod
    def _read_plaintext(path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def _read_docx(path: str) -> str:
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs])

    @staticmethod
    def _read_pdf(path: str) -> str:
        doc = pymupdf.open(path)
        return "".join([str(page.get_text()) for page in doc])

    @staticmethod
    def _read_msg(path: str) -> str:
        mail = extract_msg.Message(path)
        return f"{mail.sender} -> {mail.to}\n{mail.date}: {mail.subject}\n{mail.body}"
