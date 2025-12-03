/**
 * @fileoverview API 工具函数
 * @description 提供 API 请求的通用工具函数
 * @module shared/lib/api-utils
 * @version 1.0.0
 */

import type {
  ApiResponse,
  ApiSuccessResponse,
  ApiErrorResponse,
  PaginatedResponse,
  ISODateString,
} from '../api-types';

// ============================================================================
// API 响应处理
// ============================================================================

/**
 * 创建成功响应对象
 */
export function createSuccessResponse<T>(
  data: T,
  metadata?: Record<string, unknown>
): ApiSuccessResponse<T> {
  return {
    success: true,
    data,
    ...(metadata && { metadata }),
  };
}

/**
 * 创建错误响应对象
 */
export function createErrorResponse(
  error: string,
  details?: Record<string, unknown>
): ApiErrorResponse {
  return {
    success: false,
    error,
    details,
    timestamp: new Date().toISOString(),
  };
}

/**
 * 从 API 响应中提取数据，失败时返回 null
 */
export function extractData<T>(
  response: ApiResponse<T>
): T | null {
  if (response.success) {
    return response.data;
  }
  return null;
}

/**
 * 从 API 响应中提取数据，失败时抛出错误
 */
export function extractDataOrThrow<T>(
  response: ApiResponse<T>
): T {
  if (response.success) {
    return response.data;
  }
  throw new Error(response.error);
}

// ============================================================================
// 分页工具
// ============================================================================

/**
 * 分页配置
 */
export interface PaginationConfig {
  page: number;
  pageSize: number;
  totalCount: number;
}

/**
 * 从分页响应中提取分页信息
 */
export function extractPaginationInfo<T>(
  response: PaginatedResponse<T>,
  currentPage: number,
  pageSize: number
): PaginationConfig {
  return {
    page: currentPage,
    pageSize,
    totalCount: response.count,
  };
}

/**
 * 计算总页数
 */
export function calculateTotalPages(
  totalCount: number,
  pageSize: number
): number {
  return Math.ceil(totalCount / pageSize);
}

/**
 * 检查是否有下一页
 */
export function hasNextPage(
  currentPage: number,
  totalCount: number,
  pageSize: number
): boolean {
  return currentPage < calculateTotalPages(totalCount, pageSize);
}

/**
 * 检查是否有上一页
 */
export function hasPreviousPage(currentPage: number): boolean {
  return currentPage > 1;
}

// ============================================================================
// 数据格式化
// ============================================================================

/**
 * 格式化市值数字
 *
 * @example
 * formatMarketCap(2500000000000) // "2.50T"
 * formatMarketCap(1250000000) // "1.25B"
 * formatMarketCap(500000000) // "500M"
 */
export function formatMarketCap(
  value: number | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }

  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';

  if (absValue >= 1e12) {
    return `${sign}${(absValue / 1e12).toFixed(decimals)}T`;
  }
  if (absValue >= 1e9) {
    return `${sign}${(absValue / 1e9).toFixed(decimals)}B`;
  }
  if (absValue >= 1e6) {
    return `${sign}${(absValue / 1e6).toFixed(decimals)}M`;
  }
  if (absValue >= 1e3) {
    return `${sign}${(absValue / 1e3).toFixed(decimals)}K`;
  }
  return `${sign}${absValue.toFixed(decimals)}`;
}

/**
 * 格式化百分比
 *
 * @example
 * formatPercentage(0.3550) // "35.50%"
 * formatPercentage(-0.023) // "-2.30%"
 */
export function formatPercentage(
  value: number | null | undefined,
  decimals: number = 2,
  multiplier: number = 100
): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  return `${(value * multiplier).toFixed(decimals)}%`;
}

/**
 * 格式化数字（带千位分隔符）
 *
 * @example
 * formatNumber(1234567.89) // "1,234,567.89"
 */
export function formatNumber(
  value: number | null | undefined,
  decimals?: number
): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }

  const formatted = decimals !== undefined
    ? value.toFixed(decimals)
    : value.toString();

  const parts = formatted.split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return parts.join('.');
}

/**
 * 格式化日期
 *
 * @example
 * formatDate('2025-01-15') // "Jan 15, 2025"
 */
export function formatDate(
  value: ISODateString | Date | null | undefined,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!value) {
    return 'N/A';
  }

  const date = typeof value === 'string' ? new Date(value) : value;

  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }

  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options,
  };

  return date.toLocaleDateString('en-US', defaultOptions);
}

/**
 * 格式化日期为短格式 (用于图表)
 *
 * @example
 * formatDateShort('2025-01-15') // "Jan 2025"
 */
export function formatDateShort(
  value: ISODateString | Date | null | undefined
): string {
  return formatDate(value, { year: 'numeric', month: 'short' });
}

// ============================================================================
// URL 构建工具
// ============================================================================

/**
 * 构建带查询参数的 URL
 */
export function buildUrl(
  baseUrl: string,
  params?: Record<string, string | number | boolean | undefined | null>
): string {
  if (!params) {
    return baseUrl;
  }

  const queryParams = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value));
    }
  }

  const queryString = queryParams.toString();
  if (!queryString) {
    return baseUrl;
  }

  return `${baseUrl}${baseUrl.includes('?') ? '&' : '?'}${queryString}`;
}

// ============================================================================
// 数据比较工具
// ============================================================================

/**
 * 比较两个值并返回变化类型
 */
export type ChangeDirection = 'increase' | 'decrease' | 'unchanged';

export function compareValues(
  current: number | null | undefined,
  previous: number | null | undefined
): { direction: ChangeDirection; changePercent: number | null } {
  if (current === null || current === undefined ||
      previous === null || previous === undefined ||
      previous === 0) {
    return { direction: 'unchanged', changePercent: null };
  }

  const changePercent = ((current - previous) / Math.abs(previous)) * 100;

  if (changePercent > 0.001) {
    return { direction: 'increase', changePercent };
  }
  if (changePercent < -0.001) {
    return { direction: 'decrease', changePercent };
  }
  return { direction: 'unchanged', changePercent: 0 };
}

/**
 * 获取变化值的 CSS 类名
 */
export function getChangeColorClass(direction: ChangeDirection): string {
  switch (direction) {
    case 'increase':
      return 'text-green-600';
    case 'decrease':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
}

