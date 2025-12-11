import numpy as np

from ..config import config
from ..data import Embedding, Source
from .chunk import Chunk, chunk_text
from .model import BaseEmbeddingModel
from .model_gte import GTEEmbeddingModel
from .model_remote import RemoteEmbeddingModel


class EmbeddingFactory:
    def __init__(self):
        self._model = self.create_embedding_model()

    def create_embedding_model(self) -> BaseEmbeddingModel:
        if config.embedding_factory.process_remote:
            return RemoteEmbeddingModel()
        return GTEEmbeddingModel()

    def process(self, content: str, source: Source) -> list[Embedding]:
        assert source.id is not None, "Source ID must be set before processing."

        chunks: list[Chunk] = chunk_text(content)
        texts: list[str] = [chunk.text for chunk in chunks]
        embeddings_array: np.ndarray = self._model.encode(texts)

        return [
            Embedding(
                id=None,
                source_id=source.id,
                embedding=embedding,
                chunk_idx=chunk.idx,
            )
            for chunk, embedding in zip(chunks, embeddings_array)
        ]
