import type { SourceType } from "@/dto/sourceType";


export interface Source {
    id: number;
    source_type: SourceType;
    uri: string;
    resolved_to?: string;
    obj_created: string;
    obj_modified: string;
    last_checked: string;
    last_processed: string;
    title?: string;
}
