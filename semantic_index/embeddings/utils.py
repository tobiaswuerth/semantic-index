import numpy as np


def get_similarities(
    query_embedding: np.ndarray, all_embeddings: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    similarities = np.dot(all_embeddings, query_embedding)
    indices = np.argsort(similarities)[::-1]
    return similarities, indices
