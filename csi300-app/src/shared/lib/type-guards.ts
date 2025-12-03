/**
 * @fileoverview 运行时类型检查工具
 * @description 提供类型守卫函数，用于运行时验证 API 响应数据
 * @module shared/lib/type-guards
 * @version 1.0.0
 *
 * 使用场景:
 * - 验证 API 响应数据结构
 * - 在 TypeScript 中进行类型收窄
 * - 提供更安全的数据访问
 *
 * @example
 * import { isCSI300Company, assertValidResponse } from '@/shared/lib/type-guards';
 *
 * const response = await fetch('/api/csi300/companies/1');
 * const data = await response.json();
 *
 * if (isCSI300Company(data)) {
 *   // data 现在被类型收窄为 CSI300Company
 *   console.log(data.name);
 * }
 */

import type {
  ApiResponse,
  ApiSuccessResponse,
  ApiErrorResponse,
  PaginatedResponse,
  CSI300Company,
  CSI300InvestmentSummary,
  CSI300PeerComparisonItem,
  FredLatestValue,
  FredObservation,
  BeaIndicator,
} from '../api-types';

// ============================================================================
// 通用类型守卫
// ============================================================================

/**
 * 检查值是否为非空对象
 */
export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * 检查值是否为非空数组
 */
export function isNonEmptyArray<T>(value: unknown): value is T[] {
  return Array.isArray(value) && value.length > 0;
}

/**
 * 检查值是否为有效的 ISO 日期字符串
 */
export function isISODateString(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  const date = new Date(value);
  return !isNaN(date.getTime()) && /^\d{4}-\d{2}-\d{2}/.test(value);
}

/**
 * 检查值是否为有效的数字（包括字符串形式的数字）
 */
export function isNumericValue(value: unknown): value is number | string {
  if (typeof value === 'number' && !isNaN(value)) return true;
  if (typeof value === 'string' && value.trim() !== '' && !isNaN(Number(value))) return true;
  return false;
}

// ============================================================================
// API 响应类型守卫
// ============================================================================

/**
 * 检查是否为成功的 API 响应
 *
 * @example
 * const response = await fetchData();
 * if (isSuccessResponse(response)) {
 *   console.log(response.data);
 * }
 */
export function isSuccessResponse<T>(
  response: unknown
): response is ApiSuccessResponse<T> {
  return (
    isObject(response) &&
    response.success === true &&
    'data' in response
  );
}

/**
 * 检查是否为错误的 API 响应
 */
export function isErrorResponse(
  response: unknown
): response is ApiErrorResponse {
  return (
    isObject(response) &&
    response.success === false &&
    typeof response.error === 'string'
  );
}

/**
 * 检查是否为分页响应
 */
export function isPaginatedResponse<T>(
  response: unknown
): response is PaginatedResponse<T> {
  return (
    isObject(response) &&
    typeof response.count === 'number' &&
    Array.isArray(response.results)
  );
}

// ============================================================================
// CSI300 类型守卫
// ============================================================================

/**
 * 检查是否为有效的 CSI300 公司数据
 */
export function isCSI300Company(value: unknown): value is CSI300Company {
  if (!isObject(value)) return false;

  // 检查必需字段
  const hasRequiredFields =
    typeof value.id === 'number' &&
    typeof value.name === 'string';

  // 检查可选字段的类型（如果存在）
  const hasValidOptionalFields =
    (value.ticker === undefined || value.ticker === null || typeof value.ticker === 'string') &&
    (value.region === undefined || value.region === null || typeof value.region === 'string') &&
    (value.im_sector === undefined || value.im_sector === null || typeof value.im_sector === 'string');

  return hasRequiredFields && hasValidOptionalFields;
}

/**
 * 检查是否为有效的 CSI300 投资摘要
 */
export function isCSI300InvestmentSummary(
  value: unknown
): value is CSI300InvestmentSummary {
  if (!isObject(value)) return false;

  return (
    typeof value.company_name === 'string' &&
    typeof value.report_date === 'string' &&
    typeof value.business_overview === 'string'
  );
}

/**
 * 检查是否为有效的同行业对比项
 */
export function isCSI300PeerComparisonItem(
  value: unknown
): value is CSI300PeerComparisonItem {
  if (!isObject(value)) return false;

  return (
    typeof value.id === 'number' &&
    typeof value.name === 'string' &&
    typeof value.ticker === 'string'
  );
}

// ============================================================================
// FRED 类型守卫
// ============================================================================

/**
 * 检查是否为有效的 FRED 最新值数据
 */
export function isFredLatestValue(value: unknown): value is FredLatestValue {
  if (!isObject(value)) return false;

  return (
    typeof value.value === 'number' &&
    typeof value.date === 'string' &&
    typeof value.series_id === 'string' &&
    (value.country === 'US' || value.country === 'JP')
  );
}

/**
 * 检查是否为有效的 FRED 观测数据
 */
export function isFredObservation(value: unknown): value is FredObservation {
  if (!isObject(value)) return false;

  return (
    typeof value.date === 'string' &&
    typeof value.value === 'string'
  );
}

/**
 * 检查是否为有效的 FRED 观测数组
 */
export function isFredObservationArray(
  value: unknown
): value is FredObservation[] {
  if (!Array.isArray(value)) return false;
  return value.every(isFredObservation);
}

// ============================================================================
// BEA 类型守卫
// ============================================================================

/**
 * 检查是否为有效的 BEA 指标数据
 */
export function isBeaIndicator(value: unknown): value is BeaIndicator {
  if (!isObject(value)) return false;

  return (
    typeof value.id === 'number' &&
    typeof value.series_id === 'string' &&
    typeof value.time_period === 'string'
  );
}

// ============================================================================
// 断言函数
// ============================================================================

/**
 * 自定义类型断言错误
 */
export class TypeAssertionError extends Error {
  constructor(
    message: string,
    public readonly expectedType: string,
    public readonly actualValue: unknown
  ) {
    super(message);
    this.name = 'TypeAssertionError';
  }
}

/**
 * 断言值为指定类型，否则抛出错误
 *
 * @example
 * const data = await fetchCompany();
 * assertType(data, isCSI300Company, 'CSI300Company');
 * // data 现在是 CSI300Company 类型
 */
export function assertType<T>(
  value: unknown,
  guard: (v: unknown) => v is T,
  typeName: string
): asserts value is T {
  if (!guard(value)) {
    throw new TypeAssertionError(
      `Expected ${typeName}, got ${typeof value}`,
      typeName,
      value
    );
  }
}

/**
 * 断言 API 响应为成功响应
 *
 * @example
 * const response = await fetch('/api/...');
 * const data = await response.json();
 * assertSuccessResponse(data);
 * // data.data 现在可以安全访问
 */
export function assertSuccessResponse<T>(
  response: unknown
): asserts response is ApiSuccessResponse<T> {
  if (!isSuccessResponse<T>(response)) {
    const errorMsg = isErrorResponse(response)
      ? response.error
      : 'Unknown response format';
    throw new TypeAssertionError(
      `API request failed: ${errorMsg}`,
      'ApiSuccessResponse',
      response
    );
  }
}

// ============================================================================
// 安全访问工具
// ============================================================================

/**
 * 安全获取嵌套对象属性
 *
 * @example
 * const company = { meta: { region: 'US' } };
 * const region = safeGet(company, ['meta', 'region'], 'Unknown');
 * // region = 'US'
 */
export function safeGet<T>(
  obj: unknown,
  path: string[],
  defaultValue: T
): T {
  let current: unknown = obj;

  for (const key of path) {
    if (!isObject(current) || !(key in current)) {
      return defaultValue;
    }
    current = current[key];
  }

  return (current as T) ?? defaultValue;
}

/**
 * 安全解析数值
 */
export function safeParseNumber(
  value: unknown,
  defaultValue: number = 0
): number {
  if (typeof value === 'number' && !isNaN(value)) {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    if (!isNaN(parsed)) {
      return parsed;
    }
  }
  return defaultValue;
}

/**
 * 安全解析日期
 */
export function safeParseDate(
  value: unknown,
  defaultValue: Date | null = null
): Date | null {
  if (value instanceof Date) {
    return isNaN(value.getTime()) ? defaultValue : value;
  }
  if (typeof value === 'string') {
    const parsed = new Date(value);
    return isNaN(parsed.getTime()) ? defaultValue : parsed;
  }
  return defaultValue;
}

