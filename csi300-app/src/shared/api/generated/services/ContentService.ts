/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContentCategory } from '../models/ContentCategory';
import type { ModalContent } from '../models/ModalContent';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ContentService {
    /**
     * Content category API
     * @returns ContentCategory
     * @throws ApiError
     */
    public static apiContentCategoriesList(): CancelablePromise<Array<ContentCategory>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/categories/',
        });
    }
    /**
     * Content category API
     * @param id A unique integer value identifying this Content Category.
     * @returns ContentCategory
     * @throws ApiError
     */
    public static apiContentCategoriesRetrieve(
        id: number,
    ): CancelablePromise<ContentCategory> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/categories/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * Modal content API
     * @returns ModalContent
     * @throws ApiError
     */
    public static apiContentModalsList(): CancelablePromise<Array<ModalContent>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/modals/',
        });
    }
    /**
     * Modal content API
     * @param id A unique integer value identifying this Modal Content.
     * @returns ModalContent
     * @throws ApiError
     */
    public static apiContentModalsRetrieve(
        id: number,
    ): CancelablePromise<ModalContent> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/modals/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * Get all content - simplified version for batch retrieval
     * @returns ModalContent
     * @throws ApiError
     */
    public static apiContentModalsAllContentRetrieve(): CancelablePromise<ModalContent> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/modals/all_content/',
        });
    }
    /**
     * Get content by modal_id
     * @returns ModalContent
     * @throws ApiError
     */
    public static apiContentModalsByModalIdRetrieve(): CancelablePromise<ModalContent> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/modals/by_modal_id/',
        });
    }
}
