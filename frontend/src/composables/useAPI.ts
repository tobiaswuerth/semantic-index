const API_BASE_URL = 'http://localhost:5000/api';

import type { SearchRequest } from "@/dto/searchRequest";
import type { SearchResult } from "@/dto/searchResult";
import type { ContentResponse } from "../dto/contentResponse";
import type { TagCount } from "@/dto/tagCount";
import type { HistogramResponse, HistogramResponseString } from "@/dto/histogramResponse";

import { useFilter } from "@/composables/useFilter";

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
        },
        tag_ids: filterState.filterTags == null ? null : [...filterState.filterTags],
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
    return _search(`${API_BASE_URL}/search/chunks`, query, limit);
}

/**
 * Search for document using semantic similarity
 *
 * @param query - The search query text
 * @param limit - Maximum number of results to return
 * @returns Promise with array of search results
 */
export async function searchKnnDocsByQuery(query: string, limit: number = 10): Promise<SearchResult[]> {
    return _search(`${API_BASE_URL}/search/docs`, query, limit);
}


/**
 * Fetch content by embedding ID
 *
 * @param embeddingId - The embedding ID of the content to fetch
 * @returns Promise with content response
 */
export async function getContentByEmbeddingId(embeddingId: number): Promise<ContentResponse> {
    console.log('Fetching content for embedding ID:', embeddingId);
    return fetch(`${API_BASE_URL}/embedding/${embeddingId}/content`)
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


async function _getDateHistogram(endpoint: string): Promise<HistogramResponse[]> {
    console.log(`Fetching date histogram from endpoint: ${endpoint}`);
    return fetch(`${API_BASE_URL}/${endpoint}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch content with status: ${response.status}`);
            }
            console.log(`Date histogram fetched successfully from endpoint: ${endpoint}`);
            return response.json();
        })
        .then(histJson => {
            return histJson.map((item: HistogramResponseString) => ({
                bucket: new Date(item.bucket + "-01"),
                count: item.count
            }));
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
export async function getModifyDateHistogram(): Promise<HistogramResponse[]> {
    return _getDateHistogram('source/histogram/modifydate');
}

/**
 * Fetch created date histogram
 *
 * @returns Promise with date histogram
 */
export async function getCreateDateHistogram(): Promise<HistogramResponse[]> {
    return _getDateHistogram('source/histogram/createdate');
}

export async function getTagCounts(): Promise<TagCount[]> {
    console.log('Fetching tags from API');
    return fetch(`${API_BASE_URL}/tags`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch tags with status: ${response.status}`);
            }
            console.log('Tags fetched successfully');
            return response.json();
        })
        .catch(error => {
            console.error('Error fetching tags:', error);
            throw error;
        });
}