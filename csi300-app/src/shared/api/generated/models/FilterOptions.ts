/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for filter options response.
 */
export type FilterOptions = {
    /**
     * Available exchange codes (SSE, SZSE, HKEX)
     */
    exchanges: Array<string>;
    /**
     * Available regions
     */
    regions?: Array<string>;
    /**
     * Available IM sectors
     */
    im_sectors: Array<string>;
    /**
     * Available industries
     */
    industries: Array<string>;
    /**
     * Available GICS industries
     */
    gics_industries: Array<string>;
    /**
     * Market cap range (min/max)
     */
    market_cap_range: Record<string, any>;
    /**
     * Whether filtered by exchange
     */
    filtered_by_exchange?: boolean;
    /**
     * Whether filtered by region
     */
    filtered_by_region?: boolean;
    /**
     * Whether filtered by sector
     */
    filtered_by_sector?: boolean;
    /**
     * Current exchange filter
     */
    exchange_filter?: string | null;
    /**
     * Current region filter
     */
    region_filter?: string | null;
    /**
     * Current sector filter
     */
    sector_filter?: string | null;
};

