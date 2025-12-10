from .handler import SourceHandler
from ..data import Source


class Resolver:
    def __init__(self):
        self._handlers: list[SourceHandler] = []

    def register(self, handler: SourceHandler) -> None:
        self._handlers.append(handler)

    def find_for(self, source: Source) -> SourceHandler:
        for handler in self._handlers:
            if handler.can_handle(source.uri):
                return handler
        raise ValueError(f"No handler found for: {source.uri}")
