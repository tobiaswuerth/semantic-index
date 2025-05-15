import logging
from typing import List
import numpy as np

from semantic_index import config
from semantic_index.models import Embedding, Source

from .model import BaseEmbeddingModel
from .model_remote import RemoteEmbeddingModel
from .model_gte import GTEEmbeddingModel
from .chunk import Chunk, chunk_text


class EmbeddingFactory:
    logger = logging.getLogger(__name__)

    def __init__(self):
        if config.embedding_factory.process_remote:
            self.model: BaseEmbeddingModel = RemoteEmbeddingModel()
        else:
            self.model: BaseEmbeddingModel = GTEEmbeddingModel()

    def process(self, content: str, source: Source) -> List[Embedding]:
        assert source.id is not None, "Source ID must be set before processing."

        chunks: List[Chunk] = chunk_text(content)
        texts: List[str] = [chunk.text for chunk in chunks]
        embeddings: np.ndarray = self.model.encode(texts, progressbar=True)
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
