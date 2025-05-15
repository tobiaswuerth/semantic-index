import logging
from typing import List

from semantic_index.models import Embedding, Source

from .model import GTEEmbeddingModel
from .chunk import chunk_text


class EmbeddingFactory:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.model: GTEEmbeddingModel = GTEEmbeddingModel()

    def process(self, content: str, source: Source) -> List[Embedding]:
        assert source.id is not None, "Source ID must be set before processing."

        chunks = chunk_text(content)
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(texts, batch_size=4, progressbar=True)

        return [
            Embedding(
                id=None,
                source_id=source.id,
                embedding=embedding,
                section_from=chunk.start,
                section_to=chunk.end,
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]
