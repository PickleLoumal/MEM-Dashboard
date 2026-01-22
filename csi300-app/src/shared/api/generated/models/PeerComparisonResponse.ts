/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PeerComparisonItem } from './PeerComparisonItem';
/**
 * Serializer for the full peer comparison response.
 */
export type PeerComparisonResponse = {
    target_company: PeerComparisonItem;
    industry: string;
    comparison_data: Array<PeerComparisonItem>;
    total_top_companies_shown: number;
    total_companies_in_industry: number;
};

