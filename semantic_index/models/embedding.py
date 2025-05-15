import numpy as np
from typing import NamedTuple, Optional


class Embedding(NamedTuple):
    id: Optional[int]
    source_id: int
    embedding: np.ndarray
    section_from: int
    section_to: int
