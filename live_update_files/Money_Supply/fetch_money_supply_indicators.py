#!/usr/bin/env python3
"""
抓取Money Supply指标数据到Django数据库
基于实际使用的fetch_debt_indicators.py
"""

import os
import sys
import django
from datetime import datetime
import logging
import time

# 添加Django项目路径
sys.path.append('/Volumes/Pickle Samsung SSD/MEM Dashboard 2/src/django_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')

# 初始化Django
django.setup()

from fred_us.data_fetcher import UsFredDataFetcher
from fred_us.models import FredUsIndicator
from django.db import transaction
from django.db.utils import IntegrityError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/Volumes/Pickle Samsung SSD/MEM Dashboard 2/logs/fetch_money_supply_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MoneySupplyDataFetcher:
    """Money Supply数据抓取器类"""
    
    def __init__(self):
        self.fetcher = UsFredDataFetcher()
        self.indicators = {
            'FEDFUNDS': {
                'name': 'Federal Funds Rate',
                'type': 'Money Supply',
                'description': '联邦基金利率 - 美联储基准利率',
                'unit': 'Percent',
                'validation': {
                    'min_value': 0,
                    'max_value': 20,
                    'required_fields': ['date', 'value']
                }
            },
            'M2SL': {
                'name': 'M2 Money Supply',
                'type': 'Money Supply',
                'description': 'M2货币供应量 - 广义货币供应量',
                'unit': 'Billions of Dollars',
                'validation': {
                    'min_value': 0,
                    'max_value': None,
                    'required_fields': ['date', 'value']
                }
            },
            'WALCL': {
                'name': 'Federal Reserve Balance Sheet Total Assets',
                'type': 'Money Supply',
                'description': '美联储资产负债表总资产',
                'unit': 'Millions of U.S. Dollars',
                'validation': {
                    'min_value': 0,
                    'max_value': None,
                    'required_fields': ['date', 'value']
                }
            },
            'DRTSCIS': {
                'name': 'Bank Lending Standards',
                'type': 'Money Supply',
                'description': '银行贷款标准 - 对小企业商业贷款标准收紧的银行净百分比',
                'unit': 'Percent',
                'validation': {
                    'min_value': -100,
                    'max_value': 100,
                    'required_fields': ['date', 'value']
                }
            },
            'TOTLL': {
                'name': 'Commercial Banks Total Loans and Leases',
                'type': 'Money Supply',
                'description': '商业银行贷款和租赁总额',
                'unit': 'Billions of U.S. Dollars',
                'validation': {
                    'min_value': 0,
                    'max_value': None,
                    'required_fields': ['date', 'value']
                }
            },
            'IORB': {
                'name': 'Interest Rate on Reserve Balances',
                'type': 'Money Supply',
                'description': '准备金余额利率 - IORB利率',
                'unit': 'Percent',
                'validation': {
                    'min_value': 0,
                    'max_value': 20,
                    'required_fields': ['date', 'value']
                }
            },
            'RRPONTSYD': {
                'name': 'Overnight Reverse Repurchase Agreements',
                'type': 'Money Supply',
                'description': '隔夜逆回购协议 - 美联储临时公开市场操作出售的国债',
                'unit': 'Billions of US Dollars',
                'validation': {
                    'min_value': 0,
                    'max_value': None,
                    'required_fields': ['date', 'value']
                }
            },
            'M1SL': {
                'name': 'M1 Money Supply',
                'type': 'Money Supply',
                'description': 'M1货币供应量 - 狭义货币供应量',
                'unit': 'Billions of Dollars',
                'validation': {
                    'min_value': 0,
                    'max_value': None,
                    'required_fields': ['date', 'value']
                }
            }
        }
        
        self.stats = {
            'total_fetched': 0,
            'total_saved': 0,
            'total_errors': 0,
            'series_processed': 0,
            'start_time': datetime.now()
        }
    
    def validate_observation(self, obs, series_id):
        """验证单个观测数据"""
        try:
            # 基本字段检查
            required_fields = self.indicators[series_id]['validation']['required_fields']
            for field in required_fields:
                if field not in obs or obs[field] is None:
                    return False, f"缺少必需字段: {field}"
            
            # 值验证
            if obs['value'] == '.' or obs['value'] == '' or obs['value'] is None:
                return False, "空值"
            
            try:
                value = float(obs['value'])
            except (ValueError, TypeError):
                return False, f"无效数值: {obs['value']}"
            
            # 范围验证
            validation = self.indicators[series_id]['validation']
            if validation['min_value'] is not None and value < validation['min_value']:
                return False, f"值低于最小值: {value} < {validation['min_value']}"
            
            if validation['max_value'] is not None and value > validation['max_value']:
                return False, f"值超过最大值: {value} > {validation['max_value']}"
            
            # 日期验证
            try:
                date = datetime.strptime(obs['date'], '%Y-%m-%d').date()
                if date > datetime.now().date():
                    return False, f"未来日期: {obs['date']}"
            except ValueError:
                return False, f"无效日期格式: {obs['date']}"
            
            return True, "验证通过"
            
        except Exception as e:
            return False, f"验证异常: {str(e)}"
    
    def save_observations_batch(self, observations, series_id):
        """批量保存观测数据，包含事务处理"""
        saved_count = 0
        error_count = 0
        batch_size = 100  # 批处理大小
        
        indicator_info = self.indicators[series_id]
        
        # 分批处理数据
        for i in range(0, len(observations), batch_size):
            batch = observations[i:i + batch_size]
            
            try:
                with transaction.atomic():
                    for obs in batch:
                        # 数据验证
                        is_valid, message = self.validate_observation(obs, series_id)
                        if not is_valid:
                            logger.warning(f"{series_id} - 跳过无效数据: {message}")
                            continue
                        
                        try:
                            value = float(obs['value'])
                            date = datetime.strptime(obs['date'], '%Y-%m-%d').date()
                            
                            # 使用get_or_create避免重复
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
                                        'original_value': obs['value']
                                    }
                                }
                            )
                            
                            if created:
                                saved_count += 1
                                
                        except IntegrityError as e:
                            logger.warning(f"{series_id} - 数据重复或约束冲突: {str(e)}")
                            continue
                        except Exception as e:
                            logger.error(f"{series_id} - 保存失败: {str(e)}")
                            error_count += 1
                            continue
                
                logger.info(f"{series_id} - 批次 {i//batch_size + 1} 处理完成")
                
            except Exception as e:
                logger.error(f"{series_id} - 批次处理失败: {str(e)}")
                error_count += len(batch)
                continue
        
        return saved_count, error_count
    
    def fetch_series_with_retry(self, series_id, max_retries=3, delay=1):
        """带重试机制的数据获取"""
        for attempt in range(max_retries):
            try:
                logger.info(f"尝试获取 {series_id} (第 {attempt + 1} 次)")
                observations = self.fetcher.get_series_observations(series_id, limit=1000)
                
                if observations:
                    logger.info(f"✅ 成功获取 {series_id}: {len(observations)} 条数据")
                    return observations
                else:
                    logger.warning(f"⚠️ {series_id}: API返回空数据")
                    
            except Exception as e:
                logger.error(f"❌ {series_id} 获取失败 (尝试 {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"等待 {delay} 秒后重试...")
                    time.sleep(delay)
                    delay *= 2  # 指数退避
        
        return None
    
    def fetch_indicator(self, series_id):
        """获取单个指标数据"""
        logger.info(f"\n{'='*20} 处理指标: {series_id} {'='*20}")
        
        # 检查现有数据
        existing_count = FredUsIndicator.objects.filter(series_id=series_id).count()
        logger.info(f"数据库中现有记录数: {existing_count}")
        
        # 获取数据
        observations = self.fetch_series_with_retry(series_id)
        if not observations:
            logger.error(f"❌ {series_id}: 无法获取数据")
            self.stats['total_errors'] += 1
            return False
        
        self.stats['total_fetched'] += len(observations)
        
        # 保存数据
        logger.info(f"开始保存 {len(observations)} 条观测数据...")
        saved_count, error_count = self.save_observations_batch(observations, series_id)
        
        # 更新统计
        self.stats['total_saved'] += saved_count
        self.stats['total_errors'] += error_count
        self.stats['series_processed'] += 1
        
        # 验证保存结果
        final_count = FredUsIndicator.objects.filter(series_id=series_id).count()
        
        logger.info(f"✅ {series_id} 处理完成:")
        logger.info(f"   - 从API获取: {len(observations)} 条")
        logger.info(f"   - 新保存: {saved_count} 条")
        logger.info(f"   - 错误: {error_count} 条")
        logger.info(f"   - 数据库总计: {final_count} 条")
        
        if final_count > 0:
            latest = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
            logger.info(f"   - 最新数据: {latest.value} ({latest.date})")
        
        return True
    
    def generate_summary_report(self):
        """生成详细的执行总结报告"""
        duration = datetime.now() - self.stats['start_time']
        
        logger.info("\n" + "="*80)
        logger.info("📊 Money Supply数据抓取总结报告")
        logger.info("="*80)
        
        logger.info(f"执行时间: {duration}")
        logger.info(f"处理序列: {self.stats['series_processed']} / {len(self.indicators)}")
        logger.info(f"总获取量: {self.stats['total_fetched']} 条")
        logger.info(f"总保存量: {self.stats['total_saved']} 条")
        logger.info(f"总错误数: {self.stats['total_errors']} 条")
        
        if self.stats['total_fetched'] > 0:
            success_rate = (self.stats['total_saved'] / self.stats['total_fetched']) * 100
            logger.info(f"成功率: {success_rate:.1f}%")
        
        logger.info("\n各序列详细状态:")
        for series_id, info in self.indicators.items():
            count = FredUsIndicator.objects.filter(series_id=series_id).count()
            if count > 0:
                latest = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
                logger.info(f"✅ {series_id}: {count} 条记录 (最新: {latest.date})")
            else:
                logger.info(f"❌ {series_id}: 无数据")
    
    def run(self):
        """主执行流程"""
        logger.info(f"🚀 开始抓取Money Supply指标数据...")
        logger.info(f"📊 总共需要处理 {len(self.indicators)} 个指标")
        
        success_count = 0
        
        for series_id in self.indicators.keys():
            try:
                if self.fetch_indicator(series_id):
                    success_count += 1
                
                # 请求间隔，避免API限制
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                logger.warning("⚠️ 用户中断执行")
                break
            except Exception as e:
                logger.error(f"❌ {series_id} 处理异常: {str(e)}")
                continue
        
        # 生成总结报告
        self.generate_summary_report()
        
        # 执行结果
        if success_count == len(self.indicators):
            logger.info("🎉 所有Money Supply指标数据抓取完成")
            return True
        else:
            logger.warning(f"⚠️ 部分指标处理失败: {success_count}/{len(self.indicators)}")
            return False

def main():
    """主函数"""
    try:
        fetcher = MoneySupplyDataFetcher()
        success = fetcher.run()
        
        if success:
            logger.info("✅ Money Supply数据抓取任务成功完成")
            sys.exit(0)
        else:
            logger.error("❌ Money Supply数据抓取任务部分失败")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 系统异常: {str(e)}")
        sys.exit(2)

if __name__ == "__main__":
    main()
