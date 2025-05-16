import logging
import abc
from typing import Generator

from semantic_index.models import Source


class SourceHandler(abc.ABC):
    logger = logging.getLogger(__name__)

    def __init__(self, scheme: str):
        self.scheme = scheme

    @abc.abstractmethod
    def crawl(self, base: str) -> Generator[Source, None, None]:
        """
        Crawl the source and yield Source objects.
        """
        pass

    def read(self, source: Source) -> str:
        text = self._read_source(source)
        text = " ".join(text.split())
        return text

    @abc.abstractmethod
    def _read_source(self, source: Source) -> str:
        """
        Read the content of the source.
        """
        pass
