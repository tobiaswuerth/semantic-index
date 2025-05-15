from typing import NamedTuple


class Chunk(NamedTuple):
    start: int
    end: int
    text: str


def chunk_text(text: str, chunk_size: int = 1536, overlap: int = 768) -> list[Chunk]:
    result = []
    for start in range(0, len(text), chunk_size - overlap):
        end = min(start + chunk_size, len(text))
        chunk = Chunk(start, end, text[start:end])
        result.append(chunk)
    return result
