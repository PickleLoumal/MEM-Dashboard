#!/usr/bin/env python3
"""
Inflation指标数据抓取器
基于实际使用的fetch_banking_sector_indicators.py架构
严格遵循企业级数据处理标准

Inflation指标(8个指标):
1. CPIAUCSL - Consumer Price Index (CPI)
2. PCEPILFE - Core PCE Price Index
3. FEDFUNDS - Federal Funds Rate
4. UNRATE - Unemployment Rate
5. RSAFS - Retail Sales
6. PPIACO - Producer Price Index: All Commodities
7. T10YIEM - 10-Year Breakeven Inflation Rate
8. DCOILWTICO - Crude Oil Prices (WTI)
"""

import os
import sys
import django
from datetime import datetime, timedelta
import time
import logging
import json
from typing import Dict, List, Optional, Tuple

# 添加Django项目路径
sys.path.append('/Volumes/Pickle Samsung SSD/MEM Dashboard 2/src/django_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')

# 初始化Django
django.setup()

from fred_us.models import FredUsIndicator
from fred_us.data_fetcher import UsFredDataFetcher
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError

# 配置企业级日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/Volumes/Pickle Samsung SSD/MEM Dashboard 2/logs/fetch_inflation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InflationDataFetcher:
    """Inflation数据抓取器类"""
    
    def __init__(self):
        """初始化数据抓取器"""
        logger.info("🚀 初始化Inflation数据抓取器...")
        
        self.fetcher = UsFredDataFetcher()
        
        # Inflation指标配置 - 8个指标
        self.indicators = {
            'CPIAUCSL': {
                'name': 'Consumer Price Index (CPI)',
                'type': 'Inflation',
                'description': '消费者价格指数 - 通胀的重要衡量指标',
                'unit': 'Index 1982-1984=100',
                'validation': {
                    'min_value': 0,
                    'max_value': 1000,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'price_index'
                }
            },
            'PCEPILFE': {
                'name': 'Core PCE Price Index',
                'type': 'Inflation',
                'description': '核心个人消费支出价格指数 - 美联储关注的通胀指标',
                'unit': 'Index 2017=100',
                'validation': {
                    'min_value': 0,
                    'max_value': 500,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'price_index'
                }
            },
            'FEDFUNDS': {
                'name': 'Federal Funds Rate',
                'type': 'Inflation',
                'description': '联邦基金利率 - 影响通胀的关键货币政策工具',
                'unit': 'Percent',
                'validation': {
                    'min_value': 0,
                    'max_value': 25,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'interest_rate'
                }
            },
            'UNRATE': {
                'name': 'Unemployment Rate',
                'type': 'Inflation',
                'description': '失业率 - 与通胀有密切关系的就业指标',
                'unit': 'Percent',
                'validation': {
                    'min_value': 0,
                    'max_value': 100,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'unemployment'
                }
            },
            'RSAFS': {
                'name': 'Retail Sales',
                'type': 'Inflation',
                'description': '零售销售 - 反映消费需求和通胀压力',
                'unit': 'Millions of Dollars',
                'validation': {
                    'min_value': 0,
                    'max_value': 2000000,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'retail_sales'
                }
            },
            'PPIACO': {
                'name': 'Producer Price Index: All Commodities',
                'type': 'Inflation',
                'description': '生产者价格指数 - 上游通胀压力指标',
                'unit': 'Index 1982=100',
                'validation': {
                    'min_value': 0,
                    'max_value': 1000,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'price_index'
                }
            },
            'T10YIEM': {
                'name': '10-Year Breakeven Inflation Rate',
                'type': 'Inflation',
                'description': '10年盈亏平衡通胀率 - 市场通胀预期',
                'unit': 'Percent',
                'validation': {
                    'min_value': -5,
                    'max_value': 15,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'inflation_expectation'
                }
            },
            'DCOILWTICO': {
                'name': 'Crude Oil Prices (WTI)',
                'type': 'Inflation',
                'description': '原油价格 - 影响通胀的重要商品价格',
                'unit': 'Dollars per Barrel',
                'validation': {
                    'min_value': 0,
                    'max_value': 300,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'oil_price'
                }
            }
        }
        
        # 性能监控
        self.start_time = time.time()
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        
        logger.info(f"✅ 抓取器初始化完成，配置了{len(self.indicators)}个Inflation指标")
    
    def validate_observation(self, series_id: str, date: str, value: str) -> Tuple[bool, Optional[float], str]:
        """验证观测数据的有效性"""
        try:
            # 获取验证配置
            config = self.indicators.get(series_id, {}).get('validation', {})
            
            # 检查必需字段
            if not date or not value:
                return False, None, "缺少必需字段"
            
            # 数值转换验证
            try:
                numeric_value = float(value)
            except (ValueError, TypeError):
                if value in ['.', '', 'null', 'None']:
                    return False, None, "空值"
                return False, None, f"无效数值: {value}"
            
            # 范围验证
            min_val = config.get('min_value', float('-inf'))
            max_val = config.get('max_value', float('inf'))
            
            if not (min_val <= numeric_value <= max_val):
                return False, None, f"数值超出范围[{min_val}, {max_val}]: {numeric_value}"
            
            # 业务规则验证
            business_rule = config.get('business_rules')
            if business_rule:
                rule_valid, rule_msg = self.validate_business_rule(series_id, numeric_value, business_rule)
                if not rule_valid:
                    return False, None, f"业务规则验证失败: {rule_msg}"
            
            return True, numeric_value, "验证通过"
            
        except Exception as e:
            return False, None, f"验证异常: {str(e)}"
    
    def validate_business_rule(self, series_id: str, value: float, rule_type: str) -> Tuple[bool, str]:
        """执行业务规则验证"""
        try:
            if rule_type == 'price_index':
                # 价格指数不应该为负数，且增长应该合理
                if value < 0:
                    return False, f"价格指数不能为负: {value}"
                if value > 1000:  # 异常高的价格指数
                    return False, f"价格指数异常过高: {value}"
                return True, "价格指数合理"
                
            elif rule_type == 'interest_rate':
                # 利率验证
                if value < 0:
                    return False, f"检测到负利率: {value}%"
                if value > 25:
                    return False, f"利率异常过高: {value}%"
                return True, "利率范围合理"
                
            elif rule_type == 'unemployment':
                # 失业率验证
                if value < 0 or value > 100:
                    return False, f"失业率范围异常: {value}%"
                if value > 30:
                    return False, f"失业率异常过高: {value}%"
                return True, "失业率正常"
                
            elif rule_type == 'retail_sales':
                # 零售销售验证
                if value < 0:
                    return False, f"零售销售不能为负: {value}"
                return True, "零售销售合理"
                
            elif rule_type == 'inflation_expectation':
                # 通胀预期验证
                if value < -5 or value > 15:
                    return False, f"通胀预期范围异常: {value}%"
                return True, "通胀预期合理"
                
            elif rule_type == 'oil_price':
                # 原油价格验证
                if value < 0:
                    return False, f"原油价格不能为负: {value}"
                if value > 300:
                    return False, f"原油价格异常过高: {value}"
                return True, "原油价格合理"
            
            return True, "无特定规则"
            
        except Exception as e:
            return False, f"业务规则验证异常: {str(e)}"
    
    def save_observations_batch(self, series_id: str, observations: List[Dict]) -> Tuple[int, int]:
        """批量保存观测数据到数据库"""
        saved_count = 0
        skipped_count = 0
        
        try:
            with transaction.atomic():
                for obs in observations:
                    try:
                        # 验证数据
                        is_valid, numeric_value, validation_msg = self.validate_observation(
                            series_id, obs.get('date'), obs.get('value')
                        )
                        
                        if not is_valid:
                            skipped_count += 1
                            continue
                        
                        # 使用get_or_create避免重复
                        obj, created = FredUsIndicator.objects.get_or_create(
                            series_id=series_id,
                            date=obs['date'],
                            defaults={
                                'value': numeric_value
                            }
                        )
                        
                        if created:
                            saved_count += 1
                        else:
                            skipped_count += 1
                            
                    except IntegrityError:
                        skipped_count += 1
                        continue
                    except Exception as e:
                        logger.warning(f"保存观测数据异常 {series_id} {obs.get('date')}: {str(e)}")
                        skipped_count += 1
                        continue
                        
        except Exception as e:
            logger.error(f"批量保存事务失败 {series_id}: {str(e)}")
            raise
        
        return saved_count, skipped_count
    
    def fetch_series_with_retry(self, series_id: str, limit: int = 1000, max_retries: int = 3) -> Optional[Dict]:
        """带重试机制的系列数据获取"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 获取 {series_id} 数据 (尝试 {attempt + 1}/{max_retries})")
                
                # 使用UsFredDataFetcher的方法
                observations = self.fetcher.get_series_observations(series_id, limit=limit)
                
                if observations and len(observations) > 0:
                    logger.info(f"✅ 成功获取 {series_id}: {len(observations)} 条观测数据")
                    return {
                        'series_id': series_id,
                        'observations': observations,
                        'count': len(observations)
                    }
                else:
                    logger.warning(f"⚠️  {series_id} 未返回数据")
                    
            except Exception as e:
                logger.error(f"❌ 获取 {series_id} 失败 (尝试 {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = 2 ** attempt  # 指数退避
                    logger.info(f"⏳ 等待 {sleep_time} 秒后重试...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"💥 {series_id} 达到最大重试次数，跳过")
        
        return None
    
    def fetch_indicator(self, series_id: str) -> Dict:
        """获取单个指标数据"""
        logger.info(f"📊 开始处理指标: {series_id}")
        start_time = time.time()
        
        result = {
            'series_id': series_id,
            'success': False,
            'total_fetched': 0,
            'total_saved': 0,
            'total_skipped': 0,
            'processing_time': 0,
            'error': None
        }
        
        try:
            # 获取指标配置
            indicator_config = self.indicators.get(series_id)
            if not indicator_config:
                raise ValueError(f"未找到指标配置: {series_id}")
            
            # 获取数据
            data = self.fetch_series_with_retry(series_id, limit=1000)
            if not data:
                raise Exception(f"无法获取 {series_id} 的数据")
            
            result['total_fetched'] = data['count']
            
            # 批量保存数据
            observations = data['observations']
            batch_size = 100  # 每批处理100条
            
            total_saved = 0
            total_skipped = 0
            
            for i in range(0, len(observations), batch_size):
                batch = observations[i:i + batch_size]
                saved, skipped = self.save_observations_batch(series_id, batch)
                total_saved += saved
                total_skipped += skipped
                
                logger.info(f"📈 {series_id} 批次 {i//batch_size + 1}: 保存 {saved}, 跳过 {skipped}")
            
            result.update({
                'success': True,
                'total_saved': total_saved,
                'total_skipped': total_skipped,
                'processing_time': time.time() - start_time
            })
            
            # 更新全局统计
            self.success_count += 1
            self.processed_count += result['total_fetched']
            
            logger.info(f"✅ {series_id} 处理完成: 获取 {result['total_fetched']}, 保存 {total_saved}, 跳过 {total_skipped}")
            
        except Exception as e:
            error_msg = str(e)
            result['error'] = error_msg
            self.error_count += 1
            logger.error(f"❌ {series_id} 处理失败: {error_msg}")
        
        result['processing_time'] = time.time() - start_time
        return result
    
    def generate_summary_report(self, results: List[Dict]) -> Dict:
        """生成执行总结报告"""
        total_time = time.time() - self.start_time
        
        total_fetched = sum(r.get('total_fetched', 0) for r in results)
        total_saved = sum(r.get('total_saved', 0) for r in results)
        total_skipped = sum(r.get('total_skipped', 0) for r in results)
        
        successful_indicators = [r for r in results if r.get('success')]
        failed_indicators = [r for r in results if not r.get('success')]
        
        report = {
            'execution_summary': {
                'total_indicators': len(self.indicators),
                'successful_indicators': len(successful_indicators),
                'failed_indicators': len(failed_indicators),
                'success_rate': (len(successful_indicators) / len(self.indicators)) * 100,
                'total_execution_time': total_time,
                'average_time_per_indicator': total_time / len(self.indicators)
            },
            'data_statistics': {
                'total_records_fetched': total_fetched,
                'total_records_saved': total_saved,
                'total_records_skipped': total_skipped,
                'save_success_rate': (total_saved / total_fetched) * 100 if total_fetched > 0 else 0,
                'processing_throughput': total_fetched / total_time if total_time > 0 else 0
            },
            'indicator_details': {
                'successful': [
                    {
                        'series_id': r['series_id'],
                        'name': self.indicators[r['series_id']]['name'],
                        'fetched': r['total_fetched'],
                        'saved': r['total_saved'],
                        'processing_time': round(r['processing_time'], 2)
                    }
                    for r in successful_indicators
                ],
                'failed': [
                    {
                        'series_id': r['series_id'],
                        'name': self.indicators.get(r['series_id'], {}).get('name', 'Unknown'),
                        'error': r.get('error', 'Unknown error')
                    }
                    for r in failed_indicators
                ]
            }
        }
        
        return report
    
    def run_full_fetch(self) -> Dict:
        """执行完整的Inflation数据抓取流程"""
        logger.info("🚀 开始Inflation指标数据抓取流程")
        logger.info("="*80)
        
        results = []
        
        # 逐个处理指标
        for series_id, config in self.indicators.items():
            logger.info(f"🎯 处理指标 {series_id}: {config['name']}")
            result = self.fetch_indicator(series_id)
            results.append(result)
            
            # 短暂暂停避免API限制
            time.sleep(1)
        
        # 生成总结报告
        logger.info("="*80)
        logger.info("📊 生成执行总结报告")
        report = self.generate_summary_report(results)
        
        # 输出报告
        self.print_summary_report(report)
        
        # 保存报告到文件
        report_file = f'/Volumes/Pickle Samsung SSD/MEM Dashboard 2/logs/inflation_fetch_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 报告已保存到: {report_file}")
        except Exception as e:
            logger.error(f"❌ 保存报告失败: {str(e)}")
        
        return report
    
    def print_summary_report(self, report: Dict):
        """打印格式化的总结报告"""
        print("\n" + "="*80)
        print("📊 INFLATION 数据抓取执行总结")
        print("="*80)
        
        exec_summary = report['execution_summary']
        data_stats = report['data_statistics']
        
        print(f"🎯 指标处理概览:")
        print(f"   总指标数量: {exec_summary['total_indicators']}")
        print(f"   成功指标: {exec_summary['successful_indicators']}")
        print(f"   失败指标: {exec_summary['failed_indicators']}")
        print(f"   成功率: {exec_summary['success_rate']:.1f}%")
        
        print(f"\n⏱️  性能指标:")
        print(f"   总执行时间: {exec_summary['total_execution_time']:.2f} 秒")
        print(f"   平均处理时间: {exec_summary['average_time_per_indicator']:.2f} 秒/指标")
        print(f"   处理吞吐量: {data_stats['processing_throughput']:.1f} 条/秒")
        
        print(f"\n📈 数据统计:")
        print(f"   获取记录总数: {data_stats['total_records_fetched']:,}")
        print(f"   保存记录总数: {data_stats['total_records_saved']:,}")
        print(f"   跳过记录总数: {data_stats['total_records_skipped']:,}")
        print(f"   保存成功率: {data_stats['save_success_rate']:.1f}%")
        
        # 成功指标详情
        if report['indicator_details']['successful']:
            print(f"\n✅ 成功处理的指标:")
            for indicator in report['indicator_details']['successful']:
                print(f"   • {indicator['series_id']}: {indicator['name']}")
                print(f"     获取: {indicator['fetched']}, 保存: {indicator['saved']}, 耗时: {indicator['processing_time']}s")
        
        # 失败指标详情
        if report['indicator_details']['failed']:
            print(f"\n❌ 失败的指标:")
            for indicator in report['indicator_details']['failed']:
                print(f"   • {indicator['series_id']}: {indicator['name']}")
                print(f"     错误: {indicator['error']}")
        
        print("\n" + "="*80)

def main():
    """主执行函数"""
    try:
        logger.info("🚀 启动Inflation指标数据抓取器")
        
        # 创建并执行抓取器
        fetcher = InflationDataFetcher()
        report = fetcher.run_full_fetch()
        
        # 检查执行结果
        if report['execution_summary']['success_rate'] >= 80:
            logger.info("🎉 Inflation指标数据抓取成功完成")
            return 0
        else:
            logger.warning("⚠️  部分指标抓取失败，但整体完成")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("⚠️  用户中断执行")
        return 130
    except Exception as e:
        logger.error(f"💥 抓取过程发生严重错误: {str(e)}")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
