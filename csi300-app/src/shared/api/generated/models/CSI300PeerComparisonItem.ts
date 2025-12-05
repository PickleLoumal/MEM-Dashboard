/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for a single peer comparison item with extra fields
 */
export type CSI300PeerComparisonItem = {
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
    /**
     * Format market cap for display
     */
    readonly market_cap_display: string;
    /**
     * P/E ratio trailing
     */
    pe_ratio_trailing?: string | null;
    /**
     * Format P/E ratio for display
     */
    readonly pe_ratio_display: string;
    /**
     * Calculate and format P/B ratio for display
     */
    readonly pb_ratio_display: string;
    /**
     * ROE trailing
     */
    roe_trailing?: string | null;
    /**
     * Format ROE for display
     */
    readonly roe_display: string;
    /**
     * Calculate revenue growth for display
     */
    readonly revenue_growth_display: string;
    /**
     * Operating margin (trailing)
     */
    operating_margin_trailing?: string | null;
    /**
     * Format Operating Margin for display
     */
    readonly operating_margin_display: string;
    readonly rank: number;
    readonly is_current_company: boolean;
};

