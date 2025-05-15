import numpy as np
import requests

from semantic_index import config
from .model import BaseEmbeddingModel


class RemoteEmbeddingModel(BaseEmbeddingModel):
    def __init__(self):
        super().__init__()

    def _encode_batch(self, batch: list[str]) -> np.ndarray:
        cf = config.embedding_factory
        url = f"{cf.remote_host}:{cf.remote_port}{cf.remote_endpoint}"

        headers = {"Content-Type": "application/json"}
        data = {"batch": batch}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            embeddings = response.json()
            return np.array(embeddings)
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            raise
