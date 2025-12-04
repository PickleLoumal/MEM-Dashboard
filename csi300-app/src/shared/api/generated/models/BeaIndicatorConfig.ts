/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * BEA指标配置序列化器
 */
export type BeaIndicatorConfig = {
    readonly id: number;
    series_id: string;
    name: string;
    category?: string;
    description?: string;
    api_endpoint: string;
    table_name: string;
    line_description: string;
    units?: string;
    auto_fetch?: boolean;
    is_active?: boolean;
    priority?: number;
    fallback_value?: string | null;
    additional_config?: any;
    readonly created_at: string;
    readonly updated_at: string;
    readonly last_updated: string;
};

