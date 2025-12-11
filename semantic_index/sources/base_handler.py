import abc
import logging
from typing import Iterator

from ..data import Source
from ..data import SourceHandler as SourceHandlerModel
from ..data import SourceType as SourceTypeModel

logger = logging.getLogger(__name__)


class BaseSourceHandler(abc.ABC):
    handler_name: str = ""
    source_types: dict[str, list[str]] = {}

    def __init__(self):
        self._handler_model: SourceHandlerModel | None = None
        self._type_models: dict[str, SourceTypeModel] = {}

    def get_handler_model(self) -> SourceHandlerModel | None:
        return self._handler_model

    def set_handler_model(self, model: SourceHandlerModel) -> None:
        self._handler_model = model

    def get_type_model(self, type_name: str) -> SourceTypeModel:
        return self._type_models[type_name]

    def set_type_model(self, type_name: str, model: SourceTypeModel) -> None:
        self._type_models[type_name] = model

    @abc.abstractmethod
    def crawl(self, base: str) -> Iterator[Source]:
        pass

    def read(self, source: Source) -> str:
        text = self._read_source(source)
        return " ".join(text.split())

    @abc.abstractmethod
    def _read_source(self, source: Source) -> str:
        pass
