/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for industry peers comparison data
 */
export type CSI300IndustryPeersComparison = {
    readonly id: number;
    /**
     * Stock ticker
     */
    ticker?: string | null;
    /**
     * Company name
     */
    name: string;
    /**
     * IM Sector (combined from im_code and industry)
     */
    im_sector?: string | null;
    /**
     * Market cap (local)
     */
    market_cap_local?: string | null;
    /**
     * Market cap (USD)
     */
    market_cap_usd?: string | null;
    readonly market_cap_display: string;
    /**
     * P/E ratio trailing
     */
    pe_ratio_trailing?: string | null;
    readonly pe_ratio_display: string;
    readonly pb_ratio_display: string;
    /**
     * ROE trailing
     */
    roe_trailing?: string | null;
    readonly roe_display: string;
    readonly revenue_growth_display: string;
    /**
     * Operating margin (trailing)
     */
    operating_margin_trailing?: string | null;
    readonly operating_margin_display: string;
};

