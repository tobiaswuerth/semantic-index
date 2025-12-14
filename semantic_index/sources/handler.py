import logging

from .base_handler import BaseSourceHandler

logger = logging.getLogger(__name__)


class Handler:
    def __init__(self, handlers: list[BaseSourceHandler]):
        self.handlers_by_id: dict[int, BaseSourceHandler] = {}
        self.handlers_by_name: dict[str, BaseSourceHandler] = {}

        for handler in handlers:
            self.handlers_by_id[handler.handler.id] = handler
            self.handlers_by_name[handler.name.lower()] = handler

    def find_by_id(self, handler_id: int) -> BaseSourceHandler:
        return self.handlers_by_id[handler_id]

    def find_by_name(self, name: str) -> BaseSourceHandler:
        return self.handlers_by_name[name.lower()]
