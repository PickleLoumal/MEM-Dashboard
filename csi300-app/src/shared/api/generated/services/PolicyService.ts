/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PolicyUpdatesResponse } from '../models/PolicyUpdatesResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PolicyService {
    /**
     * Serve curated policy updates sourced from the Federal Register API.
     * @param country Country code
     * @param limit Number of results
     * @param q Search term
     * @param topicsArray Topic filters
     * @returns PolicyUpdatesResponse
     * @throws ApiError
     */
    public static apiPolicyUpdatesRetrieve(
        country?: string,
        limit?: number,
        q?: string,
        topicsArray?: string,
    ): CancelablePromise<PolicyUpdatesResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/policy/updates/',
            query: {
                'country': country,
                'limit': limit,
                'q': q,
                'topics[]': topicsArray,
            },
        });
    }
}
