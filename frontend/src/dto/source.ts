import type { Tag } from "@/dto/tag";


export interface Source {
    id: number;
    uri: string;
    resolved_to?: string;
    tags: Tag[];
    obj_created: string;
    obj_modified: string;
    last_checked: string;
    last_processed: string;
    title?: string;
}
