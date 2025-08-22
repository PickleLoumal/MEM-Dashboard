#!/usr/bin/env python3
"""
Banking Sector指标数据抓取器
基于实际使用的fetch_money_supply_indicators.py架构
严格遵循企业级数据处理标准

Banking Sector指标(8个指标):
1. FEDFUNDS - Federal Funds Rate (Effective)
2. IORB - Interest on Reserve Balances
3. TOTRESNS - Total Reserve Balances  
4. WALCL - Federal Reserve Balance Sheet (Total Assets)
5. PCEPI - PCE Price Index (Inflation)
6. UNRATE - Unemployment Rate
7. TOTLL - Commercial Bank Loans and Leases
8. DPRIME - Bank Prime Loan Rate
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
        logging.FileHandler(f'/Volumes/Pickle Samsung SSD/MEM Dashboard 2/logs/fetch_banking_sector_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BankingSectorDataFetcher:
    """
    Banking Sector数据抓取器
    实现企业级数据处理标准：
    - 事务安全性
    - 错误恢复机制  
    - 性能监控
    - 数据质量验证
    """
    
    def __init__(self):
        """初始化数据抓取器"""
        logger.info("🚀 初始化Banking Sector数据抓取器...")
        
        self.fetcher = UsFredDataFetcher()
        
        # Banking Sector指标配置 - 8个指标
        self.indicators = {
            'FEDFUNDS': {
                'name': 'Federal Funds Rate (Effective)',
                'type': 'Banking Sector',
                'description': '联邦基金利率 - 美联储货币政策基准利率',
                'unit': 'Percent',
                'validation': {
                    'min_value': 0,
                    'max_value': 25,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'interest_rate'
                }
            },
            'IORB': {
                'name': 'Interest Rate on Reserve Balances',
                'type': 'Banking Sector', 
                'description': '准备金余额利率 - 银行在美联储存款的利率',
                'unit': 'Percent',
                'validation': {
                    'min_value': 0,
                    'max_value': 25,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'interest_rate'
                }
            },
            'TOTRESNS': {
                'name': 'Total Reserve Balances',
                'type': 'Banking Sector',
                'description': '总准备金余额 - 存款机构在美联储的总准备金',
                'unit': 'Billions of Dollars',
                'validation': {
                    'min_value': 0,
                    'max_value': None,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'balance_sheet'
                }
            },
            'WALCL': {
                'name': 'Federal Reserve Balance Sheet Total Assets',
                'type': 'Banking Sector',
                'description': '美联储资产负债表总资产 - 美联储持有的总资产规模',
                'unit': 'Millions of Dollars',
                'validation': {
                    'min_value': 0,
                    'max_value': None,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'balance_sheet'
                }
            },
            'PCEPI': {
                'name': 'PCE Price Index',
                'type': 'Banking Sector',
                'description': 'PCE价格指数 - 美联储偏好的通胀指标',
                'unit': 'Index 2017=100',
                'validation': {
                    'min_value': 50,
                    'max_value': 200,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'price_index'
                }
            },
            'UNRATE': {
                'name': 'Unemployment Rate',
                'type': 'Banking Sector',
                'description': '失业率 - 劳动力市场健康度的关键指标',
                'unit': 'Percent',
                'validation': {
                    'min_value': 0,
                    'max_value': 30,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'unemployment'
                }
            },
            'TOTLL': {
                'name': 'Commercial Bank Loans and Leases',
                'type': 'Banking Sector',
                'description': '商业银行贷款和租赁 - 银行信贷活动的核心指标',
                'unit': 'Billions of Dollars',
                'validation': {
                    'min_value': 0,
                    'max_value': None,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'balance_sheet'
                }
            },
            'DPRIME': {
                'name': 'Bank Prime Loan Rate',
                'type': 'Banking Sector',
                'description': '银行基准贷款利率 - 银行向最优质客户提供的利率',
                'unit': 'Percent',
                'validation': {
                    'min_value': 0,
                    'max_value': 30,
                    'required_fields': ['date', 'value'],
                    'business_rules': 'prime_rate'
                }
            }
        }
        
        # 性能统计
        self.stats = {
            'total_fetched': 0,
            'total_saved': 0,
            'total_errors': 0,
            'series_processed': 0,
            'start_time': datetime.now(),
            'processing_times': {},
            'error_details': []
        }
        
        logger.info(f"📊 已配置 {len(self.indicators)} 个Banking Sector指标")
    
    def validate_observation(self, obs: dict, series_id: str) -> Tuple[bool, str]:
        """
        企业级数据验证
        包含多层验证：字段验证、数值验证、业务规则验证
        """
        try:
            validation_config = self.indicators[series_id]['validation']
            
            # 第一层：必需字段验证
            for field in validation_config['required_fields']:
                if field not in obs or obs[field] is None:
                    return False, f"缺少必需字段: {field}"
            
            # 第二层：数值有效性验证
            if obs['value'] == '.' or obs['value'] == '' or obs['value'] is None:
                return False, "空值或无效值"
            
            try:
                value = float(obs['value'])
            except (ValueError, TypeError):
                return False, f"无法转换为数值: {obs['value']}"
            
            # 第三层：数值范围验证
            if validation_config['min_value'] is not None and value < validation_config['min_value']:
                return False, f"值低于最小值: {value} < {validation_config['min_value']}"
            
            if validation_config['max_value'] is not None and value > validation_config['max_value']:
                return False, f"值超过最大值: {value} > {validation_config['max_value']}"
            
            # 第四层：日期格式验证
            try:
                date_obj = datetime.strptime(obs['date'], '%Y-%m-%d').date()
                if date_obj > datetime.now().date():
                    return False, f"未来日期: {obs['date']}"
            except ValueError:
                return False, f"无效日期格式: {obs['date']}"
            
            # 第五层：业务规则验证
            business_validation = self.validate_business_rules(value, series_id, validation_config['business_rules'])
            if not business_validation[0]:
                return False, f"业务规则违反: {business_validation[1]}"
            
            return True, "验证通过"
            
        except Exception as e:
            return False, f"验证异常: {str(e)}"
    
    def validate_business_rules(self, value: float, series_id: str, rule_type: str) -> Tuple[bool, str]:
        """业务规则验证"""
        try:
            if rule_type == 'interest_rate':
                # 利率业务规则
                if value < 0:
                    return False, f"负利率需要特殊关注: {value}%"
                if value > 20:
                    return False, f"异常高利率: {value}%"
                    
            elif rule_type == 'balance_sheet':
                # 资产负债表规则
                if value <= 0:
                    return False, f"资产值不能为负或零: {value}"
                    
            elif rule_type == 'price_index':
                # 价格指数规则
                if value <= 0:
                    return False, f"价格指数必须为正: {value}"
                    
            elif rule_type == 'unemployment':
                # 失业率规则
                if value < 0 or value > 100:
                    return False, f"失业率超出合理范围: {value}%"
                    
            elif rule_type == 'prime_rate':
                # 银行基准利率规则
                if value < 0:
                    return False, f"基准利率不能为负: {value}%"
                if value > 25:
                    return False, f"基准利率异常高: {value}%"
            
            return True, "业务规则验证通过"
            
        except Exception as e:
            return False, f"业务规则验证异常: {str(e)}"
    
    def save_observations_batch(self, observations: List[dict], series_id: str) -> Tuple[int, int]:
        """
        批量保存观测数据
        实现事务安全、错误恢复、性能优化
        """
        saved_count = 0
        error_count = 0
        batch_size = 100
        
        indicator_info = self.indicators[series_id]
        logger.info(f"💾 开始批量保存 {series_id}: {len(observations)} 条数据")
        
        # 分批处理以优化性能和内存使用
        for i in range(0, len(observations), batch_size):
            batch = observations[i:i + batch_size]
            batch_start_time = time.time()
            
            try:
                with transaction.atomic():
                    for obs in batch:
                        # 数据验证
                        is_valid, message = self.validate_observation(obs, series_id)
                        if not is_valid:
                            logger.debug(f"⚠️ {series_id} 跳过无效数据: {message}")
                            error_count += 1
                            continue
                        
                        try:
                            value = float(obs['value'])
                            date = datetime.strptime(obs['date'], '%Y-%m-%d').date()
                            
                            # 使用get_or_create避免重复数据
                            indicator, created = FredUsIndicator.objects.get_or_create(
                                series_id=series_id,
                                date=date,
                                defaults={
                                    'indicator_name': indicator_info['name'],
                                    'indicator_type': indicator_info['type'],
                                    'value': value,
                                    'source': 'FRED',
                                    'unit': indicator_info.get('unit', ''),
                                    'frequency': '',
                                    'metadata': {
                                        'description': indicator_info['description'],
                                        'original_value': obs['value'],
                                        'fetched_at': datetime.now().isoformat(),
                                        'validation_passed': True
                                    }
                                }
                            )
                            
                            if created:
                                saved_count += 1
                            
                        except IntegrityError as e:
                            logger.debug(f"⚠️ {series_id} 数据重复: {str(e)}")
                            continue
                        except ValidationError as e:
                            logger.warning(f"⚠️ {series_id} 数据验证失败: {str(e)}")
                            error_count += 1
                            continue
                        except Exception as e:
                            logger.error(f"❌ {series_id} 保存异常: {str(e)}")
                            error_count += 1
                            continue
                
                batch_time = time.time() - batch_start_time
                logger.debug(f"📦 {series_id} 批次 {i//batch_size + 1} 完成: {batch_time:.2f}秒")
                
            except Exception as e:
                logger.error(f"❌ {series_id} 批次事务失败: {str(e)}")
                error_count += len(batch)
                self.stats['error_details'].append({
                    'series_id': series_id,
                    'batch': i//batch_size + 1,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                continue
        
        logger.info(f"✅ {series_id} 批量保存完成: {saved_count} 新增, {error_count} 错误")
        return saved_count, error_count
    
    def fetch_series_with_retry(self, series_id: str, max_retries: int = 3, delay: float = 1.0) -> Optional[List[dict]]:
        """
        带重试机制的数据获取
        实现指数退避算法和详细错误记录
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 尝试获取 {series_id} (第 {attempt + 1}/{max_retries} 次)")
                
                # 记录请求开始时间
                request_start = time.time()
                
                # 获取更多历史数据以确保完整性
                observations = self.fetcher.get_series_observations(series_id, limit=1000)
                
                request_time = time.time() - request_start
                self.stats['processing_times'][f"{series_id}_request_{attempt+1}"] = request_time
                
                if observations:
                    logger.info(f"✅ 成功获取 {series_id}: {len(observations)} 条数据 ({request_time:.2f}秒)")
                    return observations
                else:
                    logger.warning(f"⚠️ {series_id}: API返回空数据")
                    
            except Exception as e:
                error_msg = f"{series_id} 获取失败 (尝试 {attempt + 1}): {str(e)}"
                logger.error(f"❌ {error_msg}")
                
                self.stats['error_details'].append({
                    'series_id': series_id,
                    'attempt': attempt + 1,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt)  # 指数退避
                    logger.info(f"⏳ 等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
        
        logger.error(f"💥 {series_id} 所有重试均失败")
        return None
    
    def fetch_indicator(self, series_id: str) -> bool:
        """获取单个指标的完整数据处理流程"""
        start_time = time.time()
        logger.info(f"\n{'='*50} 处理指标: {series_id} {'='*50}")
        
        try:
            # 检查现有数据
            existing_count = FredUsIndicator.objects.filter(series_id=series_id).count()
            logger.info(f"📊 数据库现有记录: {existing_count}")
            
            # 获取数据
            observations = self.fetch_series_with_retry(series_id)
            if not observations:
                logger.error(f"❌ {series_id}: 无法获取数据")
                self.stats['total_errors'] += 1
                return False
            
            self.stats['total_fetched'] += len(observations)
            
            # 数据质量预检查
            valid_data_count = sum(1 for obs in observations 
                                 if obs['value'] not in ['.', '', None])
            quality_ratio = valid_data_count / len(observations) if observations else 0
            
            logger.info(f"📈 数据质量预检: {valid_data_count}/{len(observations)} 有效数据 ({quality_ratio*100:.1f}%)")
            
            if quality_ratio < 0.8:
                logger.warning(f"⚠️ {series_id} 数据质量较低: {quality_ratio*100:.1f}%")
            
            # 保存数据
            logger.info(f"💾 开始保存 {len(observations)} 条观测数据...")
            saved_count, error_count = self.save_observations_batch(observations, series_id)
            
            # 更新统计
            self.stats['total_saved'] += saved_count
            self.stats['total_errors'] += error_count
            self.stats['series_processed'] += 1
            
            # 验证保存结果
            final_count = FredUsIndicator.objects.filter(series_id=series_id).count()
            latest_record = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
            
            processing_time = time.time() - start_time
            self.stats['processing_times'][f"{series_id}_total"] = processing_time
            
            # 详细结果报告
            logger.info(f"✅ {series_id} 处理完成:")
            logger.info(f"   📥 从API获取: {len(observations)} 条")
            logger.info(f"   💾 新保存: {saved_count} 条")
            logger.info(f"   ❌ 错误: {error_count} 条") 
            logger.info(f"   📊 数据库总计: {final_count} 条")
            logger.info(f"   ⏱️ 处理时间: {processing_time:.2f} 秒")
            
            if latest_record:
                logger.info(f"   📅 最新数据: {latest_record.value} ({latest_record.date})")
            
            return final_count > 0
            
        except Exception as e:
            logger.error(f"💥 {series_id} 处理异常: {str(e)}")
            self.stats['total_errors'] += 1
            self.stats['error_details'].append({
                'series_id': series_id,
                'error': str(e),
                'phase': 'fetch_indicator',
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def generate_comprehensive_report(self) -> dict:
        """生成详细的执行报告"""
        duration = datetime.now() - self.stats['start_time']
        
        report = {
            'execution_summary': {
                'start_time': self.stats['start_time'].isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_duration': str(duration),
                'duration_seconds': duration.total_seconds()
            },
            'processing_statistics': {
                'indicators_configured': len(self.indicators),
                'series_processed': self.stats['series_processed'],
                'total_fetched': self.stats['total_fetched'],
                'total_saved': self.stats['total_saved'],
                'total_errors': self.stats['total_errors'],
                'success_rate': (self.stats['total_saved'] / self.stats['total_fetched'] * 100) if self.stats['total_fetched'] > 0 else 0
            },
            'performance_metrics': {
                'processing_times': self.stats['processing_times'],
                'average_processing_time': sum(self.stats['processing_times'].values()) / len(self.stats['processing_times']) if self.stats['processing_times'] else 0,
                'throughput_records_per_second': self.stats['total_fetched'] / duration.total_seconds() if duration.total_seconds() > 0 else 0
            },
            'data_quality': {},
            'error_analysis': {
                'error_count': len(self.stats['error_details']),
                'error_details': self.stats['error_details']
            }
        }
        
        # 生成每个指标的详细状态
        for series_id in self.indicators.keys():
            count = FredUsIndicator.objects.filter(series_id=series_id).count()
            if count > 0:
                latest = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
                oldest = FredUsIndicator.objects.filter(series_id=series_id).order_by('date').first()
                
                report['data_quality'][series_id] = {
                    'total_records': count,
                    'latest_date': latest.date.isoformat() if latest else None,
                    'latest_value': latest.value if latest else None,
                    'oldest_date': oldest.date.isoformat() if oldest else None,
                    'data_span_days': (latest.date - oldest.date).days if latest and oldest else 0,
                    'status': 'success'
                }
            else:
                report['data_quality'][series_id] = {
                    'total_records': 0,
                    'status': 'failed'
                }
        
        return report
    
    def log_comprehensive_report(self):
        """记录详细的执行报告"""
        report = self.generate_comprehensive_report()
        
        logger.info("\n" + "="*100)
        logger.info("📊 Banking Sector数据抓取 - 综合执行报告")
        logger.info("="*100)
        
        # 执行摘要
        logger.info(f"⏰ 执行时间: {report['execution_summary']['total_duration']}")
        logger.info(f"📈 处理序列: {report['processing_statistics']['series_processed']}/{len(self.indicators)}")
        logger.info(f"📥 总获取量: {report['processing_statistics']['total_fetched']} 条")
        logger.info(f"💾 总保存量: {report['processing_statistics']['total_saved']} 条")
        logger.info(f"❌ 总错误数: {report['processing_statistics']['total_errors']} 条")
        logger.info(f"✅ 成功率: {report['processing_statistics']['success_rate']:.1f}%")
        
        # 性能指标
        logger.info(f"⚡ 平均处理时间: {report['performance_metrics']['average_processing_time']:.2f} 秒")
        logger.info(f"🚀 处理吞吐量: {report['performance_metrics']['throughput_records_per_second']:.1f} 条/秒")
        
        # 各指标详细状态
        logger.info("\n📋 各指标详细状态:")
        for series_id, info in self.indicators.items():
            quality_info = report['data_quality'].get(series_id, {})
            if quality_info.get('status') == 'success':
                logger.info(f"✅ {series_id}: {quality_info['total_records']} 条记录")
                logger.info(f"   📅 时间范围: {quality_info['oldest_date']} 到 {quality_info['latest_date']}")
                logger.info(f"   📈 最新值: {quality_info['latest_value']}")
            else:
                logger.info(f"❌ {series_id}: 抓取失败")
        
        # 错误分析
        if report['error_analysis']['error_count'] > 0:
            logger.warning(f"\n⚠️ 错误分析: 共发现 {report['error_analysis']['error_count']} 个错误")
            for error in report['error_analysis']['error_details'][-5:]:  # 显示最近5个错误
                logger.warning(f"   - {error.get('series_id', 'Unknown')}: {error.get('error', 'Unknown error')}")
    
    def run(self) -> bool:
        """主执行流程"""
        logger.info("🚀 开始Banking Sector指标数据抓取...")
        logger.info(f"📊 目标指标: {list(self.indicators.keys())}")
        logger.info(f"🎯 预期抓取: {len(self.indicators)} 个系列")
        
        success_count = 0
        
        try:
            for series_id in self.indicators.keys():
                try:
                    if self.fetch_indicator(series_id):
                        success_count += 1
                    
                    # API请求间隔，避免速率限制
                    time.sleep(0.5)
                    
                except KeyboardInterrupt:
                    logger.warning("⚠️ 用户中断执行")
                    break
                except Exception as e:
                    logger.error(f"❌ {series_id} 处理异常: {str(e)}")
                    continue
            
            # 生成综合报告
            self.log_comprehensive_report()
            
            # 执行结果判断
            if success_count == len(self.indicators):
                logger.info("🎉 所有Banking Sector指标数据抓取完成")
                return True
            else:
                logger.warning(f"⚠️ 部分指标处理失败: {success_count}/{len(self.indicators)}")
                return success_count > 0  # 只要有一个成功就算部分成功
                
        except Exception as e:
            logger.error(f"💥 系统级异常: {str(e)}")
            return False

def main():
    """主函数"""
    logger.info("="*100)
    logger.info("Banking Sector FRED数据抓取器 v2.0")
    logger.info("企业级数据处理 | 事务安全 | 性能监控")
    logger.info("="*100)
    
    try:
        fetcher = BankingSectorDataFetcher()
        success = fetcher.run()
        
        if success:
            logger.info("✅ Banking Sector数据抓取任务完成")
            sys.exit(0)
        else:
            logger.error("❌ Banking Sector数据抓取任务失败")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 系统异常: {str(e)}")
        sys.exit(2)

if __name__ == "__main__":
    main()
