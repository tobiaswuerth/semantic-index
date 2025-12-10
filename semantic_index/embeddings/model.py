import abc
import math
from typing import Sequence
import numpy as np
from tqdm import tqdm

from ..config import config


class BaseEmbeddingModel(abc.ABC):
    def encode(
        self,
        texts: str | Sequence[str],
        *,
        show_progress: bool = False,
    ) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        batch_size = config.embedding_factory.batch_size
        num_texts = len(texts)
        num_batches = math.ceil(num_texts / batch_size)

        iterator = range(0, num_texts, batch_size)
        if show_progress:
            iterator = tqdm(iterator, total=num_batches, desc="Encoding")

        embeddings = []
        for i in iterator:
            batch = texts[i : i + batch_size]
            embeddings.append(self._encode_batch(list(batch)))

        return np.vstack(embeddings)

    @abc.abstractmethod
    def _encode_batch(self, batch: list[str]) -> np.ndarray:
        pass
