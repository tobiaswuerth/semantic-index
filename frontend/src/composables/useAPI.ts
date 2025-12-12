const API_BASE_URL = 'http://localhost:5000';

import type { SearchRequest } from "@/dto/searchRequest";
import type { SearchResult } from "@/dto/searchResult";
import { useFilter } from "@/composables/useFilter";
import type { ContentResponse } from "../dto/contentResponse";


async function _search(target_url: string, query: string, limit: number = 10): Promise<SearchResult[]> {
    console.log(`Searching url: ${target_url}, query: ${query}, limit: ${limit}`);

    const filterState = useFilter().state;
    const body: SearchRequest = {
        query,
        limit,
        date_filter: {
            createdate_start: filterState.filterCreateDateRange?.startDate ?? null,
            createdate_end: filterState.filterCreateDateRange?.endDate ?? null,
            modifieddate_start: filterState.filterModifyDateRange?.startDate ?? null,
            modifieddate_end: filterState.filterModifyDateRange?.endDate ?? null,
        }
    };
    console.log('Search request body:', body);

    return fetch(target_url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    }).then(response => {
        if (!response.ok) {
            throw new Error(`Search failed with status: ${response.status}`);
        }
        console.log(`Search response received from url: ${target_url}`);
        return response.json();
    }).catch(error => {
        console.error('Error in semantic search:', error);
        throw error;
    });
}

/**
 * Search for document chunks using semantic similarity
 *
 * @param query - The search query text
 * @param limit - Maximum number of results to return
 * @returns Promise with array of search results
 */
export async function searchKnnChunksByQuery(query: string, limit: number = 10): Promise<SearchResult[]> {
    return _search(`${API_BASE_URL}/api/search_knn_chunks_by_query`, query, limit);
}

/**
 * Search for document using semantic similarity
 *
 * @param query - The search query text
 * @param limit - Maximum number of results to return
 * @returns Promise with array of search results
 */
export async function searchKnnDocsByQuery(query: string, limit: number = 10): Promise<SearchResult[]> {
    return _search(`${API_BASE_URL}/api/search_knn_docs_by_query`, query, limit);
}


/**
 * Fetch content by embedding ID
 *
 * @param embeddingId - The embedding ID of the content to fetch
 * @returns Promise with content response
 */
export async function getContentByEmbeddingId(embeddingId: number): Promise<ContentResponse> {
    console.log('Fetching content for embedding ID:', embeddingId);
    return fetch(`${API_BASE_URL}/api/read_content_by_embedding_id/${embeddingId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch content with status: ${response.status}`);
            }
            console.log('Content fetched successfully for embedding ID:', embeddingId);
            return response.json();
        })
        .catch(error => {
            console.error('Error fetching content by embedding ID:', error);
            throw error;
        });
}


async function _getDateHistogram(endpoint: string): Promise<[Date, number][]> {
    console.log(`Fetching date histogram from endpoint: ${endpoint}`);
    return fetch(`${API_BASE_URL}/api/${endpoint}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch content with status: ${response.status}`);
            }
            console.log(`Date histogram fetched successfully from endpoint: ${endpoint}`);
            return response.json();
        })
        .then(histJson => {
            return histJson.map((item: any) => ([new Date(item[0] + "-01"), item[1]]));
        })
        .catch(error => {
            console.error(`Error fetching date histogram from endpoint ${endpoint}:`, error);
            throw error;
        });
}

/**
 * Fetch modified date histogram
 *
 * @returns Promise with date histogram
 */
export async function getModifyDateHistogram(): Promise<[Date, number][]> {
    return _getDateHistogram('get_modifydate_histogram');
}

/**
 * Fetch created date histogram
 *
 * @returns Promise with date histogram
 */
export async function getCreateDateHistogram(): Promise<[Date, number][]> {
    return _getDateHistogram('get_createdate_histogram');
}