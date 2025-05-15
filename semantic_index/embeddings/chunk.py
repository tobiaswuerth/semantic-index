from typing import NamedTuple


class Chunk(NamedTuple):
    start: int
    end: int
    text: str


def chunk_text(text: str, chunk_size: int = 1536, overlap: int = 512) -> list[Chunk]:
    """
    Split text into overlapping chunks of specified size.

    Args:
        text: The input text to chunk
        chunk_size: The maximum size of each chunk
        overlap: The number of characters to overlap between chunks

    Returns:
        A list of Chunk objects containing start position, end position, and text
    """
    assert chunk_size > 0, "chunk_size must be greater than 0"
    assert overlap >= 0, "overlap must be greater than or equal to 0"
    assert overlap < chunk_size, "overlap must be less than chunk_size"

    if not text:
        return []

    text_length = len(text)
    stride = chunk_size - overlap
    if text_length <= chunk_size:
        return [Chunk(0, text_length, text)]

    start = 0
    result = []
    while start < text_length:
        end = min(start + chunk_size, text_length)
        result.append(Chunk(start, end, text[start:end]))
        start += stride

    return result
