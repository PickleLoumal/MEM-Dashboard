/**
 * @fileoverview CSI300 公司详情页 API 服务模块
 * @module pages/detail/api
 * @description 提供 CSI300 指数成分股公司详情数据的获取接口，
 *              包括公司基本信息、财务指标和同行业对比数据。
 * @version 1.1.0
 * @author MEM Dashboard Team
 *
 * @example
 * // 基本使用
 * import { fetchCompanyDetail, fetchPeersComparison } from './api';
 *
 * // 获取公司详情
 * const company = await fetchCompanyDetail('600519');
 *
 * // 获取同行业对比
 * const peers = await fetchPeersComparison('600519');
 */

import { CompanyDetail, PeerComparisonData } from './types';
import { Csi300Service } from '../../shared/api/generated';

// Note: OpenAPI.BASE is configured in main.tsx before this module is imported

/**
 * 获取 CSI300 公司详细信息
 *
 * 从后端 API 获取指定公司的完整详情数据，包括：
 * - 基本信息（股票代码、名称、行业分类）
 * - 市场数据（股价、市值、52周高低）
 * - 财务指标（营收、利润、资产负债）
 * - 估值指标（PE、PEG、ROE、ROA）
 * - 风险指标（债务比率、流动比率、Altman Z-Score）
 * - 股息信息（股息率、派息比率、CAGR）
 *
 * @async
 * @function fetchCompanyDetail
 * @param {string} id - 公司唯一标识符（数据库 ID 或股票代码）
 * @returns {Promise<CompanyDetail>} 公司详情数据对象
 * @throws {Error} 当 HTTP 请求失败时抛出错误
 */
export async function fetchCompanyDetail(id: string): Promise<CompanyDetail> {
  // Generated client expects number ID
  // Note: The generated client handles errors and returns the parsed JSON
  // We cast the result to CompanyDetail to maintain compatibility with existing components
  // (The generated type CSI300Company is structure-compatible with CompanyDetail)
  return await Csi300Service.apiCsi300ApiCompaniesRetrieve(Number(id)) as unknown as CompanyDetail;
}

/**
 * 获取同行业公司对比数据
 *
 * 获取目标公司与同行业前3名公司的关键指标对比，用于：
 * - 行业内排名分析
 * - 竞争对手比较
 * - 估值水平对比
 *
 * 返回数据包括：
 * - 目标公司在行业内的排名
 * - 行业内公司总数
 * - 前3名公司的对比数据（市值、PE、ROE、营业利润率）
 *
 * @async
 * @function fetchPeersComparison
 * @param {string} id - 目标公司唯一标识符（数据库 ID）
 * @returns {Promise<PeerComparisonData>} 同行业对比数据对象
 * @throws {Error} 当 HTTP 请求失败或公司不存在时抛出错误
 */
export async function fetchPeersComparison(id: string): Promise<PeerComparisonData> {
  // Generated client expects number ID
  // We cast the result to PeerComparisonData to maintain compatibility
  // (The generated type CSI300PeerComparisonResponse is structure-compatible with PeerComparisonData)
  return await Csi300Service.apiCsi300ApiCompaniesIndustryPeersComparisonRetrieve(Number(id)) as unknown as PeerComparisonData;
}
