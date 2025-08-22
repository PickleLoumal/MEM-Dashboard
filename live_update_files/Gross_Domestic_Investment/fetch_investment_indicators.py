#!/usr/bin/env python3
"""
BEA投资指标数据抓取器
从BEA API获取Gross Domestic Investment相关指标数据并存储到Django数据库

基于真实的BEA API结构和现有数据库配置
"""

import os
import sys
import django
from datetime import datetime, timedelta
import time
import logging
import urllib.request
import urllib.parse
import json

# 添加Django项目路径
sys.path.append('/Volumes/Pickle Samsung SSD/MEM Dashboard 2/src/django_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')

# 初始化Django
django.setup()

from bea.models import BeaIndicator, BeaIndicatorConfig
from django.db import transaction
from django.db.utils import IntegrityError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/Volumes/Pickle Samsung SSD/MEM Dashboard 2/logs/fetch_investment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BeaInvestmentDataFetcher:
    """BEA投资数据抓取器类"""
    
    def __init__(self):
        self.api_key = "DEFB02B6-33E9-4803-AEC1-73B03F4084B8"
        self.base_url = "https://apps.bea.gov/api/data"
        
        # 投资指标配置 - 基于测试结果的有效指标
        self.indicators = {
            'INVESTMENT_TOTAL': {
                'table_name': 'T10101',
                'line_number': 7,
                'name': 'Gross Private Domestic Investment',
                'description': 'Gross private domestic investment',
                'category': 'investment',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            },
            'INVESTMENT_FIXED': {
                'table_name': 'T10101', 
                'line_number': 8,
                'name': 'Fixed Investment',
                'description': 'Fixed investment',
                'category': 'investment',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            },
            'INVESTMENT_NONRESIDENTIAL': {
                'table_name': 'T10101',
                'line_number': 9,
                'name': 'Nonresidential Investment',
                'description': 'Nonresidential fixed investment',
                'category': 'investment',
                'units': 'Percent change from preceding period', 
                'dataset_name': 'NIPA'
            },
            'INVESTMENT_RESIDENTIAL': {
                'table_name': 'T10101',
                'line_number': 10,
                'name': 'Residential Investment',
                'description': 'Residential fixed investment',
                'category': 'investment',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            },
            'INVESTMENT_INVENTORIES': {
                'table_name': 'T10101',
                'line_number': 11,
                'name': 'Change in Private Inventories',
                'description': 'Change in private inventories',
                'category': 'investment',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            },
            'INVESTMENT_STRUCTURES': {
                'table_name': 'T10101',
                'line_number': 12,
                'name': 'Structures',
                'description': 'Structures',
                'category': 'investment',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            },
            'INVESTMENT_EQUIPMENT': {
                'table_name': 'T10101',
                'line_number': 13,
                'name': 'Equipment',
                'description': 'Equipment',
                'category': 'investment',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            },
            'INVESTMENT_IP': {
                'table_name': 'T10101',
                'line_number': 14,
                'name': 'Intellectual Property Products',
                'description': 'Intellectual property products',
                'category': 'investment',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            },
            'GOVT_TOTAL': {
                'table_name': 'T10101',
                'line_number': 21,
                'name': 'Government Consumption and Investment',
                'description': 'Government consumption expenditures and gross investment',
                'category': 'government',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            },
            'GOVT_FEDERAL': {
                'table_name': 'T10101',
                'line_number': 22,
                'name': 'Federal Government Spending',
                'description': 'Federal government spending',
                'category': 'government',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            },
            'GOVT_STATE_LOCAL': {
                'table_name': 'T10101',
                'line_number': 35,
                'name': 'State and Local Government Spending',
                'description': 'State and local government spending',
                'category': 'government',
                'units': 'Percent change from preceding period',
                'dataset_name': 'NIPA'
            }
        }
        
        self.stats = {
            'total_fetched': 0,
            'total_saved': 0,
            'total_errors': 0,
            'series_processed': 0,
            'start_time': datetime.now()
        }

    def fetch_bea_data(self, table_name, line_number, series_id, years='2020,2021,2022,2023,2024,2025'):
        """从BEA API获取数据"""
        params = {
            'UserID': self.api_key,
            'method': 'GetData',
            'datasetname': 'NIPA',
            'TableName': table_name,
            'LineNumber': str(line_number),
            'Year': years,
            'Frequency': 'Q',
            'ResultFormat': 'JSON'
        }
        
        try:
            query_string = urllib.parse.urlencode(params)
            full_url = f"{self.base_url}?{query_string}"
            
            logger.info(f"正在从BEA API获取 {series_id} 数据...")
            logger.debug(f"API URL: {full_url}")
            
            with urllib.request.urlopen(full_url) as response:
                bea_data = json.loads(response.read().decode())
            
            if 'BEAAPI' in bea_data:
                beaapi = bea_data['BEAAPI']
                
                # 检查错误
                if 'Error' in beaapi:
                    logger.error(f"BEA API错误: {beaapi['Error']}")
                    return None
                
                # 获取数据
                if 'Results' in beaapi and 'Data' in beaapi['Results']:
                    data_points = beaapi['Results']['Data']
                    logger.info(f"✅ {series_id}: 从API获取到 {len(data_points)} 个数据点")
                    return data_points
                else:
                    logger.warning(f"⚠️ {series_id}: API响应格式错误")
                    return None
            else:
                logger.error(f"❌ {series_id}: 无效的API响应")
                return None
                
        except Exception as e:
            logger.error(f"❌ {series_id}: 数据获取失败 - {e}")
            return None

    def parse_time_period(self, time_period):
        """解析BEA时间格式 (例如: 2024Q1) 转换为日期"""
        try:
            year = int(time_period[:4])
            quarter = int(time_period[5:])
            
            # 季度对应月份的映射
            quarter_months = {1: 3, 2: 6, 3: 9, 4: 12}
            month = quarter_months.get(quarter, 12)
            
            # 使用季度最后一天作为日期
            if month == 3:
                day = 31
            elif month == 6:
                day = 30
            elif month == 9:
                day = 30
            else:  # 12月
                day = 31
            
            return datetime(year, month, day).date()
        except:
            logger.error(f"无法解析时间格式: {time_period}")
            return None

    def save_indicator_data(self, series_id, data_points, indicator_info):
        """保存指标数据到数据库"""
        saved_count = 0
        error_count = 0
        
        try:
            with transaction.atomic():
                for data_point in data_points:
                    try:
                        # 解析数据
                        time_period = data_point.get('TimePeriod')
                        data_value = data_point.get('DataValue')
                        
                        # 跳过无效数据
                        if not time_period or not data_value or data_value == '--':
                            continue
                        
                        # 转换数值
                        try:
                            value = float(data_value)
                        except (ValueError, TypeError):
                            logger.warning(f"无效数值: {data_value} for {series_id} at {time_period}")
                            continue
                        
                        # 解析日期
                        date = self.parse_time_period(time_period)
                        if not date:
                            continue
                        
                        # 检查是否已存在
                        if BeaIndicator.objects.filter(
                            series_id=series_id,
                            time_period=time_period
                        ).exists():
                            continue
                        
                        # 创建新记录
                        indicator = BeaIndicator(
                            series_id=series_id,
                            indicator_name=indicator_info['name'],
                            indicator_type=indicator_info['category'],
                            table_name=indicator_info['table_name'],
                            line_number=str(indicator_info['line_number']),
                            date=date,
                            time_period=time_period,
                            value=value,
                            source='BEA',
                            unit=indicator_info['units'],
                            frequency='Q',
                            dataset_name=indicator_info['dataset_name'],
                            metadata={
                                'description': indicator_info['description'],
                                'api_fetched': datetime.now().isoformat()
                            }
                        )
                        indicator.save()
                        saved_count += 1
                        
                    except Exception as e:
                        logger.error(f"保存单条记录失败 {series_id}: {e}")
                        error_count += 1
                        continue
                
                logger.info(f"✅ {series_id}: 成功保存 {saved_count} 条新记录")
                if error_count > 0:
                    logger.warning(f"⚠️ {series_id}: {error_count} 条记录保存失败")
                
                return saved_count, error_count
                
        except Exception as e:
            logger.error(f"❌ {series_id}: 数据库事务失败 - {e}")
            return 0, len(data_points)

    def ensure_indicator_config(self, series_id, indicator_info):
        """确保指标配置存在于数据库中"""
        try:
            config, created = BeaIndicatorConfig.objects.get_or_create(
                series_id=series_id,
                defaults={
                    'name': indicator_info['name'],
                    'description': indicator_info['description'],
                    'table_name': indicator_info['table_name'],
                    'line_description': indicator_info['description'],
                    'line_number': indicator_info['line_number'],
                    'units': indicator_info['units'],
                    'frequency': 'Q',
                    'years': '2020,2021,2022,2023,2024,2025',
                    'category': indicator_info['category'],
                    'api_endpoint': series_id.lower().replace('_', '-'),
                    'is_active': True,
                    'auto_fetch': True,
                    'dataset_name': indicator_info['dataset_name'],
                    'created_by': 'fetch_script',
                    'updated_by': 'fetch_script'
                }
            )
            
            if created:
                logger.info(f"✅ 创建新配置: {series_id}")
            else:
                logger.debug(f"配置已存在: {series_id}")
                
            return config
            
        except Exception as e:
            logger.error(f"❌ 配置创建失败 {series_id}: {e}")
            return None

    def fetch_indicator(self, series_id):
        """获取单个指标数据"""
        logger.info(f"\n{'='*20} 处理指标: {series_id} {'='*20}")
        
        indicator_info = self.indicators[series_id]
        
        # 确保配置存在
        config = self.ensure_indicator_config(series_id, indicator_info)
        if not config:
            logger.error(f"❌ {series_id}: 无法创建指标配置")
            return False
        
        # 检查现有数据
        existing_count = BeaIndicator.objects.filter(series_id=series_id).count()
        logger.info(f"数据库现有记录: {existing_count}")
        
        # 获取数据
        data_points = self.fetch_bea_data(
            indicator_info['table_name'], 
            indicator_info['line_number'], 
            series_id
        )
        
        if not data_points:
            logger.error(f"❌ {series_id}: 无法获取数据")
            self.stats['total_errors'] += 1
            return False
        
        self.stats['total_fetched'] += len(data_points)
        
        # 保存数据
        saved_count, error_count = self.save_indicator_data(series_id, data_points, indicator_info)
        
        # 更新统计
        self.stats['total_saved'] += saved_count
        self.stats['total_errors'] += error_count
        self.stats['series_processed'] += 1
        
        # 验证保存结果
        final_count = BeaIndicator.objects.filter(series_id=series_id).count()
        if final_count > 0:
            latest = BeaIndicator.objects.filter(series_id=series_id).order_by('-date').first()
            logger.info(f"📊 {series_id} 总记录数: {final_count}")
            logger.info(f"📊 最新数据: {latest.value} ({latest.time_period})")
        
        return True

    def generate_summary_report(self):
        """生成详细的执行总结报告"""
        duration = datetime.now() - self.stats['start_time']
        
        logger.info("\n" + "="*80)
        logger.info("📊 BEA投资指标数据抓取总结报告")
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
            count = BeaIndicator.objects.filter(series_id=series_id).count()
            if count > 0:
                latest = BeaIndicator.objects.filter(series_id=series_id).order_by('-date').first()
                logger.info(f"✅ {series_id}: {count} 条记录 (最新: {latest.time_period})")
            else:
                logger.info(f"❌ {series_id}: 无数据")

    def run(self):
        """主执行流程"""
        logger.info(f"🚀 开始抓取BEA投资指标数据...")
        logger.info(f"📊 总共需要处理 {len(self.indicators)} 个指标")
        
        success_count = 0
        
        for series_id in self.indicators.keys():
            try:
                if self.fetch_indicator(series_id):
                    success_count += 1
                
                # 请求间隔，避免API限制
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.warning("⚠️ 用户中断执行")
                break
            except Exception as e:
                logger.error(f"❌ {series_id} 处理异常: {e}")
                continue
        
        # 生成总结报告
        self.generate_summary_report()
        
        # 执行结果
        if success_count == len(self.indicators):
            logger.info("🎉 所有投资指标数据抓取完成")
            return True
        else:
            logger.warning(f"⚠️ 部分指标处理失败: {success_count}/{len(self.indicators)}")
            return False

def main():
    """主函数"""
    try:
        logger.info("=" * 60)
        logger.info("BEA投资指标数据抓取器启动")
        logger.info("=" * 60)
        
        fetcher = BeaInvestmentDataFetcher()
        success = fetcher.run()
        
        if success:
            logger.info("✅ 数据抓取任务成功完成")
            sys.exit(0)
        else:
            logger.error("❌ 数据抓取任务部分失败")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 系统异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(2)

if __name__ == "__main__":
    main()

