import type { Source } from "@/dto/source";
import type { Embedding } from "@/dto/embedding";

export interface SearchResult {
    source: Source;
    embedding: Embedding;
    similarity: number;
}

