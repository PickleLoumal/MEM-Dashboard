#!/usr/bin/env python3
"""
BEA Table 5.2.6投资指标数据抓取器
从BEA API获取Real Gross and Net Domestic Investment by Major Type数据并存储到Django数据库

基于成功测试的BEA Table 5.2.6 (T50206) 年度数据
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
        logging.FileHandler(f'/Volumes/Pickle Samsung SSD/MEM Dashboard 2/logs/fetch_bea_table526_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BeaTable526DataFetcher:
    """BEA Table 5.2.6投资数据抓取器类"""
    
    def __init__(self):
        self.api_key = "DEFB02B6-33E9-4803-AEC1-73B03F4084B8"
        self.base_url = "https://apps.bea.gov/api/data"
        self.table_name = "T50206"  # 经测试成功的表名
        
        # 基于CSV文件真实结构的投资指标配置
        self.indicators = {
            'INVESTMENT_TOTAL': {
                'line_number': 4,
                'name': 'Gross Private Domestic Investment',
                'description': 'Gross private domestic investment',
                'category': 'investment',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            },
            'INVESTMENT_FIXED': {
                'line_number': 7,
                'name': 'Fixed Investment',
                'description': 'Fixed investment',
                'category': 'investment',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            },
            'INVESTMENT_NONRESIDENTIAL': {
                'line_number': 10,
                'name': 'Nonresidential Investment',
                'description': 'Nonresidential fixed investment',
                'category': 'investment',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            },
            'INVESTMENT_STRUCTURES': {
                'line_number': 13,
                'name': 'Structures',
                'description': 'Structures',
                'category': 'investment',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            },
            'INVESTMENT_EQUIPMENT': {
                'line_number': 16,
                'name': 'Equipment',
                'description': 'Equipment',
                'category': 'investment',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            },
            'INVESTMENT_IP': {
                'line_number': 19,
                'name': 'Intellectual Property Products',
                'description': 'Intellectual property products',
                'category': 'investment',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            },
            'INVESTMENT_RESIDENTIAL': {
                'line_number': 22,
                'name': 'Residential Investment',
                'description': 'Residential fixed investment',
                'category': 'investment',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            },
            'INVESTMENT_INVENTORIES': {
                'line_number': 25,
                'name': 'Change in Private Inventories',
                'description': 'Change in private inventories',
                'category': 'investment',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            },
            'INVESTMENT_NET': {
                'line_number': 6,
                'name': 'Net Private Domestic Investment',
                'description': 'Equals: Net private domestic investment',
                'category': 'investment',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            },
            'GOVT_INVESTMENT_TOTAL': {
                'line_number': 26,
                'name': 'Gross Government Investment',
                'description': 'Gross government investment',
                'category': 'government',
                'units': 'Millions of Chained 2017 Dollars',
                'frequency': 'A'
            }
        }
        
        self.stats = {
            'total_fetched': 0,
            'total_saved': 0,
            'total_errors': 0,
            'series_processed': 0,
            'start_time': datetime.now()
        }

    def fetch_bea_data(self, line_number, series_id, years='2000,2005,2010,2015,2020,2021,2022,2023,2024'):
        """从BEA API获取Table 5.2.6数据"""
        params = {
            'UserID': self.api_key,
            'method': 'GetData',
            'datasetname': 'NIPA',
            'TableName': self.table_name,
            'LineNumber': str(line_number),
            'Year': years,
            'Frequency': 'A',  # 年度数据
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
                    all_data_points = beaapi['Results']['Data']
                    logger.info(f"✅ {series_id}: 从API获取到 {len(all_data_points)} 个数据点 (整个表格)")
                    
                    # 过滤出指定行号的数据 - 修复核心问题
                    target_line_data = []
                    for data in all_data_points:
                        data_line_number = data.get('LineNumber', '')
                        if data_line_number == str(line_number):
                            target_line_data.append(data)
                    
                    if target_line_data:
                        logger.info(f"✅ {series_id}: 过滤出行 {line_number} 的数据: {len(target_line_data)} 个数据点")
                        return target_line_data
                    else:
                        logger.warning(f"⚠️ {series_id}: 未找到行 {line_number} 的数据")
                        # 显示可用的行号用于调试
                        available_lines = set()
                        for data in all_data_points[:10]:  # 只显示前10个以避免日志过长
                            available_lines.add(data.get('LineNumber', 'N/A'))
                        logger.debug(f"可用行号 (前10个): {sorted(available_lines)}")
                        return None
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
        """解析BEA时间格式 (例如: 2023) 转换为日期"""
        try:
            year = int(time_period)
            # 使用年末日期
            return datetime(year, 12, 31).date()
        except:
            logger.error(f"无法解析时间格式: {time_period}")
            return None

    def save_indicator_data(self, series_id, data_points, indicator_info):
        """保存指标数据到数据库 - 保存所有有效的数据点"""
        saved_count = 0
        error_count = 0

        try:
            with transaction.atomic():
                # 处理所有有效的数据点（现在data_points已经是过滤后的正确行号数据）
                for data_point in data_points:
                    try:
                        # 解析数据
                        time_period = data_point.get('TimePeriod')
                        data_value = data_point.get('DataValue')

                        # 跳过无效数据
                        if not time_period or not data_value or data_value == '--':
                            continue

                        # 转换数值 - 移除逗号并转换为浮点数
                        try:
                            clean_value = str(data_value).replace(',', '')
                            value = float(clean_value)
                        except (ValueError, TypeError):
                            logger.warning(f"无法转换数值 {series_id}: {data_value}")
                            error_count += 1
                            continue

                        # 解析日期
                        date = self.parse_time_period(time_period)
                        if not date:
                            error_count += 1
                            continue

                        # 检查是否已存在相同series_id和日期的记录，如果存在则更新
                        existing_record = BeaIndicator.objects.filter(
                            series_id=series_id,
                            date=date
                        ).first()

                        if existing_record:
                            # 更新现有记录
                            existing_record.value = value
                            existing_record.date = date
                            existing_record.time_period = time_period
                            existing_record.metadata.update({
                                'description': indicator_info['description'],
                                'table_5_2_6': True,
                                'api_fetched': datetime.now().isoformat(),
                                'raw_value': data_value,
                                'updated': True
                            })
                            existing_record.save()
                            logger.info(f"✅ {series_id}: 更新现有记录 {time_period} - 值: {value}")
                        else:
                            # 创建新记录
                            indicator = BeaIndicator(
                                series_id=series_id,
                                indicator_name=indicator_info['name'],
                                indicator_type=indicator_info['category'],
                                table_name=self.table_name,
                                line_number=str(indicator_info['line_number']),
                                date=date,
                                time_period=time_period,
                                value=value,
                                source='BEA',
                                unit=indicator_info['units'],
                                frequency=indicator_info['frequency'],
                                dataset_name='NIPA',
                                metadata={
                                    'description': indicator_info['description'],
                                    'table_5_2_6': True,
                                    'api_fetched': datetime.now().isoformat(),
                                    'raw_value': data_value
                                }
                            )
                            indicator.save()
                            logger.info(f"✅ {series_id}: 创建新记录 {time_period} - 值: {value}")

                        saved_count += 1

                    except Exception as e:
                        logger.error(f"保存记录失败 {series_id} {time_period}: {e}")
                        error_count += 1

                logger.info(f"✅ {series_id}: 处理完成 - 保存 {saved_count} 条，失败 {error_count} 条")
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
                    'table_name': self.table_name,
                    'line_description': indicator_info['description'],
                    'line_number': indicator_info['line_number'],
                    'units': indicator_info['units'],
                    'frequency': indicator_info['frequency'],
                    'years': '2000,2005,2010,2015,2020,2021,2022,2023,2024',
                    'category': indicator_info['category'],
                    'api_endpoint': series_id.lower().replace('_', '-'),
                    'is_active': True,
                    'auto_fetch': True,
                    'dataset_name': 'NIPA',
                    'created_by': 'fetch_table526_script',
                    'updated_by': 'fetch_table526_script',
                    'additional_config': {
                        'table_5_2_6': True,
                        'chained_2017_dollars': True
                    }
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
        logger.info("📊 BEA Table 5.2.6投资指标数据抓取总结报告")
        logger.info("="*80)
        
        logger.info(f"执行时间: {duration}")
        logger.info(f"表格: {self.table_name} (Real Gross and Net Domestic Investment)")
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
        logger.info(f"🚀 开始抓取BEA Table 5.2.6投资指标数据...")
        logger.info(f"📊 表格: {self.table_name}")
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
        logger.info("BEA Table 5.2.6投资指标数据抓取器启动")
        logger.info("=" * 60)
        
        fetcher = BeaTable526DataFetcher()
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

