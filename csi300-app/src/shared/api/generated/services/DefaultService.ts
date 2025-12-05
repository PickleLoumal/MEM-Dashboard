/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiRootResponse } from '../models/ApiRootResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * 根路径 - API欢迎信息
     * @returns ApiRootResponse
     * @throws ApiError
     */
    public static rootRetrieve(): CancelablePromise<ApiRootResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }
}
