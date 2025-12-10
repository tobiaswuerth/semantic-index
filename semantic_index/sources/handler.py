import abc
import logging
from typing import Iterator

from ..data.models import Source

logger = logging.getLogger(__name__)


class SourceHandler(abc.ABC):
    def __init__(self, scheme: str):
        self.scheme = scheme

    def can_handle(self, uri: str) -> bool:
        return uri.startswith(self.scheme)

    @abc.abstractmethod
    def crawl(self, base: str) -> Iterator[Source]:
        pass

    def read(self, source: Source) -> str:
        text = self._read_source(source)
        return " ".join(text.split())

    @abc.abstractmethod
    def _read_source(self, source: Source) -> str:
        pass
