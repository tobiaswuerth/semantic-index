import logging
import os
from datetime import datetime
from typing import Callable, Iterator
import docx
import extract_msg
import pymupdf

from ..data.models import Source
from .handler import SourceHandler

logger = logging.getLogger(__name__)


class FileSourceHandler(SourceHandler):
    def __init__(self):
        super().__init__(scheme="file:///")
        self._readers: dict[str, Callable[[str], str]] = {
            ".txt": self._read_plaintext,
            ".md": self._read_plaintext,
            ".csv": self._read_plaintext,
            ".docx": self._read_docx,
            ".pdf": self._read_pdf,
            ".msg": self._read_msg,
        }

    def crawl(self, base: str) -> Iterator[Source]:
        for root, _, files in os.walk(base):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in self._readers:
                    continue

                path = os.path.join(root, file)
                last_modified = datetime.fromtimestamp(os.path.getmtime(path))
                yield Source(
                    id=None,
                    uri=self.scheme + path.replace("\\", "/"),
                    last_modified=last_modified,
                    last_processed=None,
                    error=False,
                    error_message=None,
                )

    def _read_source(self, source: Source) -> str:
        ext = os.path.splitext(source.uri)[1].lower()
        reader = self._readers[ext]
        path = source.uri[len(self.scheme) :]
        return reader(path)

    @staticmethod
    def _read_plaintext(path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def _read_docx(path: str) -> str:
        doc = docx.Document(path)
        return "\n".join(para.text for para in doc.paragraphs)

    @staticmethod
    def _read_pdf(path: str) -> str:
        doc = pymupdf.open(path)
        return "".join(page.get_text() for page in doc)

    @staticmethod
    def _read_msg(path: str) -> str:
        mail = extract_msg.Message(path)
        return f"{mail.sender} -> {mail.to}\n{mail.date}: {mail.subject}\n{mail.body}"
