/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContentTypeEnum } from './ContentTypeEnum';
/**
 * Modal content serializer
 */
export type ModalContent = {
    readonly id: number;
    /**
     * Modal ID used by frontend, e.g.: motor-vehicles
     */
    modal_id: string;
    /**
     * Title displayed in the modal
     */
    title: string;
    /**
     * Detailed description displayed in the modal
     */
    description: string;
    /**
     * Explanation of why this indicator/content is important
     */
    importance: string;
    /**
     * Source of the data
     */
    source: string;
    /**
     * Category this content belongs to
     */
    category?: number | null;
    readonly category_name: string;
    /**
     * Specific type of content
     *
     * * `consumer-spending` - Consumer Spending
     * * `motor-vehicles` - Motor Vehicles
     * * `services-exports` - Services Exports
     * * `goods-exports` - Goods Exports
     * * `economic-indicators` - Economic Indicators
     * * `investment-components` - Investment Components
     * * `market-analysis` - Market Analysis
     */
    content_type: ContentTypeEnum;
    readonly breakdown: Array<Record<string, any>>;
    /**
     * Whether to display in frontend
     */
    is_active?: boolean;
    /**
     * Lower number = higher priority
     */
    priority?: number;
    readonly created_at: string;
    readonly updated_at: string;
};

