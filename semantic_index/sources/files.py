import logging
from typing import Generator
import os
from datetime import datetime
import pymupdf
import docx
import extract_msg

from .handler import SourceHandler, Source


class FileSourceHandler(SourceHandler):

    def __init__(self):
        super().__init__(scheme="file:///")
        self.extensions = {
            ".txt": FileSourceHandler._read_plaintext,
            ".md": FileSourceHandler._read_plaintext,
            ".csv": FileSourceHandler._read_plaintext,
            ".docx": FileSourceHandler._read_docx,
            ".pdf": FileSourceHandler._read_pdf,
            ".msg": FileSourceHandler._read_msg,
        }

    def crawl(self, base: str) -> Generator[Source, None, None]:
        for root, _, files in os.walk(base):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in self.extensions:
                    continue

                self.logger.debug(f"Crawler detected file: {file}")
                path = os.path.join(root, file)
                last_modified = datetime.fromtimestamp(os.path.getmtime(path))
                yield Source(
                    id=None,
                    uri=self.scheme + path.replace("\\", "/"),
                    last_modified=last_modified,
                    last_processed=None,
                )

    def _read_source(self, source: Source) -> str | None:
        ext = os.path.splitext(source.uri)[1]
        reader = self.extensions[ext]
        path = source.uri[len(self.scheme) :]
        text = reader(path)
        return text

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
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    @staticmethod
    def _read_msg(path: str) -> str:
        mail = extract_msg.Message(path)
        return (
            f"{mail.sender} -> {mail.to}\n"
            f"{mail.date}: {mail.subject}\n"
            f"{mail.body}"
        )
