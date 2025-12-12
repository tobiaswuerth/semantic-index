import type { SearchDateFilter } from "./searchDateFilter";

export interface SearchRequest {
    query: string;
    limit: number;
    date_filter: SearchDateFilter;
}
