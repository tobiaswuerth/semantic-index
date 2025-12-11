export interface SourceTypeSchema {
    id: number;
    name: string;
    source_handler_id: number;
}

export interface Source {
    id: number;
    source_type: SourceTypeSchema;
    uri: string;
    resolved_to?: string;
    obj_created: string;
    obj_modified: string;
    last_checked: string;
    last_processed: string;
    title?: string;
}

export interface KnnSearchResult {
    source: Source;
    similarity: number;
    embedding_id: number;
}

export interface ContentResponse {
    section: string;
}

const API_BASE_URL = 'http://localhost:5000';

/**
 * Search for document chunks using semantic similarity
 *
 * @param query - The search query text
 * @param limit - Maximum number of results to return
 * @returns Promise with array of search results
 */
export async function searchKnnChunksByQuery(query: string, limit: number = 10): Promise<KnnSearchResult[]> {
    return fetch(`${API_BASE_URL}/api/search_knn_chunks_by_query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query,
            limit,
        }),
    }).then(response => {
        if (!response.ok) {
            throw new Error(`Search failed with status: ${response.status}`);
        }
        return response.json();
    }).catch(error => {
        console.error('Error in semantic search:', error);
        throw error;
    });
}

/**
 * Search for document using semantic similarity
 *
 * @param query - The search query text
 * @param limit - Maximum number of results to return
 * @returns Promise with array of search results
 */
export async function searchKnnDocsByQuery(query: string, limit: number = 10): Promise<KnnSearchResult[]> {
    return fetch(`${API_BASE_URL}/api/search_knn_docs_by_query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query,
            limit,
        }),
    }).then(response => {
        if (!response.ok) {
            throw new Error(`Search failed with status: ${response.status}`);
        }
        return response.json();
    }).catch(error => {
        console.error('Error in semantic search:', error);
        throw error;
    });
}

export async function getContentByEmbeddingId(embeddingId: number): Promise<ContentResponse> {
    const response = await fetch(`${API_BASE_URL}/api/read_content_by_embedding_id/${embeddingId}`);

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch content: ${errorText}`);
    }

    return await response.json();
}
