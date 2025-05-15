from typing import List

from semantic_index.models import Source
from .handler import SourceHandler


class Resolver:
    def __init__(self):
        self.handler: List[SourceHandler] = []

    def register(self, handler: SourceHandler):
        self.handler.append(handler)

    def find_for(self, source: Source) -> SourceHandler:
        """
        Get the source handler for a given source.
        """
        for h in self.handler:
            if source.uri.startswith(h.scheme):
                return h

        assert False, f"Source handler not found for {source.uri}"
