import abc
import logging
from typing import Iterator

from ..data import Source, SourceHandlerRepository, TagRepository

logger = logging.getLogger(__name__)


class BaseSourceHandler(abc.ABC):
    def __init__(
        self,
        repo_source_handler: SourceHandlerRepository,
        repo_tag: TagRepository,
    ):
        self.name = self.get_name()
        self.handler = repo_source_handler.get_or_create(self.name)
        assert self.handler

        self.repo_tag = repo_tag
        self.handler_tag = self.repo_tag.get_or_create(self.name)
        assert self.handler_tag

    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    @abc.abstractmethod
    def index_all(self, base: str) -> Iterator[Source]:
        pass

    @abc.abstractmethod
    def index_one(self, uri: str) -> Source:
        pass

    def read(self, source: Source) -> str:
        text = self._read_source(source)
        assert isinstance(text, str), "Read source must return a string"
        return " ".join(text.split())

    @abc.abstractmethod
    def _read_source(self, source: Source) -> str:
        pass
