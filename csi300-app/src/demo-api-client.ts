import { CSI300Service, CSI300Company } from '../shared/api/generated';

/**
 * 这是一个演示脚本，展示如何使用自动生成的 API 客户端。
 * 
 * 注意: 这个脚本仅用于验证类型安全性和 API 连接性。
 * 在实际应用中，你应该在组件中使用这些服务。
 */

async function demo() {
  try {
    console.log('Fetching CSI300 companies...');
    
    // 使用生成的服务获取公司列表
    // 注意：这里所有的参数都是类型安全的
    const response = await CSI300Service.apiCsi300ApiCompaniesList({
      page: 1,
      pageSize: 10,
      region: 'Mainland China'
    });
    
    console.log(`Successfully fetched ${response.count} companies.`);
    
    if (response.results && response.results.length > 0) {
      const firstCompany = response.results[0];
      console.log('First company:', firstCompany.name, firstCompany.ticker);
      
      // 类型安全演示：尝试访问不存在的字段会在编译时报错
      // console.log(firstCompany.non_existent_field); // TS Error: Property 'non_existent_field' does not exist
      
      // 访问存在的字段
      if (firstCompany.market_cap_local) {
        console.log(`Market Cap: ${firstCompany.market_cap_local}`);
      }
    }
    
  } catch (error) {
    console.error('API Error:', error);
  }
}

// 如果在非浏览器环境中运行 (如 ts-node)，取消注释下面一行
// demo();

export default demo;

