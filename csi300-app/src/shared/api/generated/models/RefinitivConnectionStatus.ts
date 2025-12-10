/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Refinitiv 连接状态序列化器。
 */
export type RefinitivConnectionStatus = {
    /**
     * 是否已认证
     */
    authenticated: boolean;
    /**
     * 凭证是否已配置
     */
    credentials_configured: boolean;
    /**
     * 错误信息
     */
    error?: string | null;
};

