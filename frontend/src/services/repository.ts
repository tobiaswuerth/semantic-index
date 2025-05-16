export interface Source {
    id: number;
    uri: string;
    last_modified: string;
    last_processed: string | null;
    error: number;
    error_message: string | null;
}

export interface KnnSearchResult {
    source: Source;
    similarity: number;
}

const API_BASE_URL = 'http://localhost:5000';

/**
 * Search for documents using semantic similarity
 * 
 * @param query - The search query text
 * @param limit - Maximum number of results to return
 * @returns Promise with array of search results
 */
export async function semanticSearch(query: string, limit: number = 5): Promise<KnnSearchResult[]> {
    return fetch(`${API_BASE_URL}/api/search_knn_by_query`, {
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
