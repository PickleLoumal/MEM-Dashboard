/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for filter options
 */
export type CSI300FilterOptions = {
    regions?: Array<string>;
    im_sectors: Array<string>;
    industries: Array<string>;
    gics_industries: Array<string>;
    market_cap_range: Record<string, any>;
    filtered_by_region?: boolean;
    filtered_by_sector?: boolean;
    region_filter?: string | null;
    sector_filter?: string | null;
};

