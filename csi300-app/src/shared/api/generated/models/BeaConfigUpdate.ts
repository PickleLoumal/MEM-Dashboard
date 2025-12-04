/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 更新BEA配置的序列化器
 */
export type BeaConfigUpdate = {
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
};

