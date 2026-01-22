/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request serializer for triggering Daily Briefing workflow
 */
export type DailyBriefingTrigger = {
    /**
     * If true, only run Stage 1 (scraping) without triggering Stage 2 (AI generation)
     */
    scrape_only?: boolean;
};

