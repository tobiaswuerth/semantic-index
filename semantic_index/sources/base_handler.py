import abc
import logging
from typing import Iterator

from ..data import Source, SourceHandler, SourceType

logger = logging.getLogger(__name__)


class BaseSourceHandler(abc.ABC):
    handler_name: str = ""
    source_types: dict[str, list[str]] = {}

    def __init__(self):
        self.source_handler: SourceHandler | None = None
        self.source_types_by_name: dict[str, SourceType] = {}

    def get_handler(self) -> SourceHandler | None:
        return self.source_handler

    def set_handler(self, model: SourceHandler) -> None:
        self.source_handler = model

    def source_type_by_name(self, type_name: str) -> SourceType:
        return self.source_types_by_name[type_name]

    def set_source_type(self, type_name: str, model: SourceType) -> None:
        self.source_types_by_name[type_name] = model

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
