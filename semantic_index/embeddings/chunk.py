from typing import NamedTuple, List


class Chunk(NamedTuple):
    idx: int
    text: str

def chunk_text(text: str, size: int = 1536, hard_cut: bool = False, overlap: bool = True) -> list[Chunk]:
    """
    Splits a text into chunks of a specified maximum size, with options for
    handling word boundaries and overlapping chunks.

    Args:
        text: The input string to be chunked.
        size: The maximum desired character length for each chunk.
        hard_cut: If True, chunks can cut mid-word to strictly enforce the size limit.
                  If False, chunks respect word boundaries, meaning a chunk might be
                  slightly shorter than 'size' if adding the next word would exceed it.
        overlap: If True, consecutive chunks will overlap.
                 In hard_cut mode, the overlap is approximately half the chunk size.
                 In word boundary mode, the overlap tries to include roughly half
                 the character size of the previous chunk, measured from the end.
                 If False, chunks are consecutive and non-overlapping.

    Returns:
        A list of text chunks.

    Raises:
        AssertionError: If input types are incorrect or constraints are violated.
    """
    # 1. Input Validation
    assert isinstance(text, str), "text must be a string"
    assert isinstance(size, int), "size must be an integer"
    assert isinstance(hard_cut, bool), "hard_cut must be a boolean"
    assert isinstance(overlap, bool), "overlap must be a boolean"
    assert size > 0, "size must be greater than 0"

    # 2. Preprocessing - Normalize whitespace
    text = " ".join(text.split())
    text_length = len(text)
    assert text_length > 0, "text must not be empty"

    # 3. Edge Case: Text is already smaller than chunk size
    if text_length <= size:
        return [Chunk(0, text)]

    chunks = []

    # 4. Hard Cut Logic (cuts anywhere)
    if hard_cut:
        # Determine the step size: full size for no overlap, half size for overlap
        step = max(1, size // 2 if overlap else size) # Ensure step is at least 1

        for i in range(0, text_length, step):
            chunk = text[i : i + size].strip()
            if chunk: # Only add non-empty chunks
                chunks.append(chunk)
        # The last chunk might be shorter and is implicitly handled by the slice
        # Handle potential overlap creating identical last chunks if step is small vs remaining text
        if len(chunks) > 1 and overlap and chunks[-1] == chunks[-2]:
             chunks.pop()
        # Ensure the very end of the text is included if missed by the steps
        if not text.endswith(chunks[-1][-10:] if chunks else ''): # Heuristic check
             start_of_last = text.rfind(chunks[-1]) if chunks else 0
             if start_of_last + len(chunks[-1]) < text_length:
                  final_chunk_start = max(text_length - size, start_of_last + step) # Try to overlap based on step
                  final_chunk = text[final_chunk_start:].strip()
                  if final_chunk and (not chunks or final_chunk != chunks[-1]):
                      chunks.append(final_chunk)


    # 5. Word Boundary Logic
    else:
        words = text.split()
        num_words = len(words)
        current_word_idx = 0

        while current_word_idx < num_words:
            current_chunk_words = []
            current_chunk_len = 0
            last_word_idx_in_chunk = current_word_idx -1 # Initialize before loop

            # Build the chunk word by word
            for i in range(current_word_idx, num_words):
                word = words[i]
                word_len = len(word)
                # Calculate length if word is added (account for space)
                len_if_added = current_chunk_len + word_len + (1 if current_chunk_words else 0)

                if len_if_added <= size:
                    current_chunk_words.append(word)
                    current_chunk_len = len_if_added
                    last_word_idx_in_chunk = i
                else:
                    # If the very first word is already too long, add it anyway
                    if i == current_word_idx:
                         current_chunk_words.append(word)
                         current_chunk_len = word_len
                         last_word_idx_in_chunk = i
                    # Stop adding words to this chunk
                    break

            # If no words could be added (e.g., empty input after split?), break outer loop
            if not current_chunk_words:
                 break

            # Join the words and add the chunk
            chunk_str = " ".join(current_chunk_words)
            chunks.append(chunk_str)

            # Check if we've processed all words
            if last_word_idx_in_chunk >= num_words - 1:
                break

            # Determine the start of the next chunk
            if overlap:
                # Target an overlap of roughly half the size
                target_overlap_len = size // 2
                overlap_achieved_len = 0
                next_start_word_idx = last_word_idx_in_chunk # Default to minimal overlap

                # Iterate backwards from the end of the current chunk
                for i in range(last_word_idx_in_chunk, current_word_idx, -1):
                    word = words[i]
                    overlap_achieved_len += len(word) + 1 # Add 1 for space
                    # If the accumulated overlap length reaches the target,
                    # the *next* word (i) is where the next chunk should start
                    if overlap_achieved_len >= target_overlap_len:
                        next_start_word_idx = i
                        break
                    # If we went too far back and included the starting word,
                    # we must advance by at least one. Set next start to word after current start.
                    next_start_word_idx = i


                # Ensure we always advance by at least one word to prevent infinite loops
                current_word_idx = max(next_start_word_idx, current_word_idx + 1)

            else: # No overlap, start next chunk after the last word of the current one
                current_word_idx = last_word_idx_in_chunk + 1

    # Filter out any potential empty strings again just in case
    return [Chunk(idx, chunk) for idx, chunk in enumerate(chunks) if chunk]