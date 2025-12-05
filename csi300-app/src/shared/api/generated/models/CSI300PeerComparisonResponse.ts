/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CSI300PeerComparisonItem } from './CSI300PeerComparisonItem';
/**
 * Serializer for the full peer comparison response
 */
export type CSI300PeerComparisonResponse = {
    target_company: CSI300PeerComparisonItem;
    industry: string;
    comparison_data: Array<CSI300PeerComparisonItem>;
    total_top_companies_shown: number;
    total_companies_in_industry: number;
};

