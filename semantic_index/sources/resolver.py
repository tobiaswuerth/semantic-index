import logging

from .base_handler import BaseSourceHandler
from ..data import Source, SourceHandlerRepository, SourceTypeRepository

logger = logging.getLogger(__name__)


class Resolver:
    def __init__(
        self,
        handler_repo: SourceHandlerRepository | None = None,
        type_repo: SourceTypeRepository | None = None,
    ):
        self._handlers: dict[int, BaseSourceHandler] = {}
        self._handler_repo = handler_repo or SourceHandlerRepository()
        self._type_repo = type_repo or SourceTypeRepository()

    def register(self, handler: BaseSourceHandler) -> None:
        handler_model = self._handler_repo.get_or_create(handler.handler_name)
        handler.set_handler_model(handler_model)
        logger.info(f"Registered handler: {handler.handler_name} (id={handler_model.id})")

        for type_name in handler.source_types.keys():
            type_model = self._type_repo.get_or_create(type_name, handler_model.id)
            handler.set_source_type(type_name, type_model)
            logger.info(f"  Registered type: {type_name} (id={type_model.id})")

        self._handlers[handler_model.id] = handler

    def find_for(self, source: Source) -> BaseSourceHandler:
        handler = self._handlers.get(source.source_handler_id)
        if handler is None:
            raise ValueError(
                f"No handler registered for source_handler_id={source.source_handler_id} "
                f"(source: {source.uri})"
            )
        return handler

    def get_handler_by_id(self, handler_id: int) -> BaseSourceHandler | None:
        return self._handlers.get(handler_id)

    def get_handler_by_name(self, name: str) -> BaseSourceHandler | None:
        name = name.strip().lower()
        for handler in self._handlers.values():
            if handler.handler_name.lower() == name:
                return handler
        return None

    def get_handlers(self) -> list[BaseSourceHandler]:
        return list(self._handlers.values())
