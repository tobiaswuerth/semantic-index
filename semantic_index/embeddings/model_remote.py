import logging
import numpy as np
import requests

from .model import BaseEmbeddingModel
from ..config import config

logger = logging.getLogger(__name__)


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
            logger.error(f"Remote embedding request failed: {e}")
            raise
