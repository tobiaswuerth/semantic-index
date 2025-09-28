import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class Embedding:
    id: Optional[int]
    source_id: int
    embedding: np.ndarray
    chunk_idx: int
