import logging
import abc
from typing import Generator

from semantic_index.models import Source


class SourceHandler(abc.ABC):
    logger = logging.getLogger(__name__)

    @abc.abstractmethod
    def crawl(self, base: str) -> Generator[Source, None, None]:
        """
        Crawl the source and yield Source objects.
        """
        pass

    def read(self, source: Source) -> str | None:
        try:
            text = self._read_source(source)
            if text is None:
                self.logger.warning(f"Failed to read source: {source.uri}")
                return None

            # clean text
            text = " ".join(text.split())
            self.logger.debug(f"Read {len(text)} characters from {source.uri}")
            return text
        except Exception as e:
            self.logger.error(f"Error reading source {source.uri}: {e}")
            return None

    @abc.abstractmethod
    def _read_source(self, source: Source) -> str | None:
        """
        Read the content of the source.
        """
        pass
