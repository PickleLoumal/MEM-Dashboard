/**
 * @fileoverview CSI300 公司详情页 API 服务模块
 * @module pages/detail/api
 * @description 提供 CSI300 指数成分股公司详情数据的获取接口，
 *              包括公司基本信息、财务指标和同行业对比数据。
 * @version 1.0.0
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

/**
 * API 基础地址
 * @constant {string}
 * @description 从环境变量 VITE_API_BASE 获取，默认为 'http://localhost:8001'
 */
const API_BASE = (import.meta.env.VITE_API_BASE || 'http://localhost:8001').replace(/\/$/, '');

/**
 * 公司详情端点模板
 * @constant {string}
 */
const COMPANY_DETAIL_ENDPOINT = '/api/csi300/api/companies/{id}/';

/**
 * 同行业对比端点模板
 * @constant {string}
 */
const PEERS_COMPARISON_ENDPOINT = '/api/csi300/api/companies/{id}/industry_peers_comparison/';

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
 * @throws {Error} 当 HTTP 请求失败时抛出错误，包含状态码和状态文本
 * 
 * @example
 * // 使用数据库 ID 获取公司详情
 * try {
 *   const detail = await fetchCompanyDetail('1');
 *   console.log(detail.name);           // "贵州茅台"
 *   console.log(detail.ticker);         // "600519"
 *   console.log(detail.market_cap_usd); // 250000000000
 *   console.log(detail.pe_ratio_trailing); // 35.5
 * } catch (error) {
 *   console.error('获取公司详情失败:', error.message);
 * }
 * 
 * @example
 * // 在 React 组件中使用
 * const [company, setCompany] = useState<CompanyDetail | null>(null);
 * 
 * useEffect(() => {
 *   fetchCompanyDetail(companyId)
 *     .then(setCompany)
 *     .catch(console.error);
 * }, [companyId]);
 * 
 * @see {@link CompanyDetail} 返回数据结构定义
 * @see {@link https://api.example.com/docs/csi300} API 文档
 */
export async function fetchCompanyDetail(id: string): Promise<CompanyDetail> {
  const url = `${API_BASE}${COMPANY_DETAIL_ENDPOINT.replace('{id}', id)}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
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
 * 
 * @example
 * // 获取茅台的同行业对比数据
 * try {
 *   const peers = await fetchPeersComparison('1');
 *   
 *   // 查看目标公司排名
 *   console.log(`行业排名: ${peers.target_company.rank}`);
 *   console.log(`行业公司总数: ${peers.total_companies_in_industry}`);
 *   
 *   // 遍历对比数据
 *   peers.comparison_data.forEach(company => {
 *     console.log(`${company.name}: PE=${company.pe_ratio_display}, ROE=${company.roe_display}`);
 *     if (company.is_current_company) {
 *       console.log('  ↑ 当前查看的公司');
 *     }
 *   });
 * } catch (error) {
 *   console.error('获取对比数据失败:', error.message);
 * }
 * 
 * @example
 * // 响应数据结构示例
 * {
 *   target_company: { rank: 1 },
 *   industry: "Consumer Staples",
 *   total_companies_in_industry: 25,
 *   comparison_data: [
 *     {
 *       name: "贵州茅台",
 *       ticker: "600519",
 *       rank: 1,
 *       is_current_company: true,
 *       market_cap_display: "2.50T",
 *       pe_ratio_display: "35.50",
 *       roe_display: "32.50%"
 *     },
 *     // ... 其他公司
 *   ]
 * }
 * 
 * @see {@link PeerComparisonData} 返回数据结构定义
 */
export async function fetchPeersComparison(id: string): Promise<PeerComparisonData> {
  const url = `${API_BASE}${PEERS_COMPARISON_ENDPOINT.replace('{id}', id)}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}
