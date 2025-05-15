import abc
import logging
import math
import numpy as np
from tqdm import tqdm

from semantic_index import config


class BaseEmbeddingModel(abc.ABC):
    logger = logging.getLogger(__name__)

    def encode(
        self,
        texts: list[str],
        progressbar: bool = False,
    ) -> np.ndarray:
        batch_size = config.embedding_factory.batch_size
        self.logger.info(f"Encoding {len(texts)} texts with batch size {batch_size}...")
        if isinstance(texts, str):
            texts = [texts]

        num_texts = len(texts)
        iter = range(0, num_texts, batch_size)
        if progressbar:
            iter = tqdm(iter, total=math.ceil(num_texts / batch_size))

        embeddings = []
        for i in iter:
            batch = texts[i : i + batch_size]
            embeddings.append(self._encode_batch(batch))

        self.logger.info("Encoding completed.")
        if progressbar:
            iter.close()
        return np.vstack(embeddings)

    @abc.abstractmethod
    def _encode_batch(self, batch: list[str]) -> np.ndarray:
        pass
