#!/usr/bin/env python3
"""
验证BEA Table 5.2.6投资指标数据库数据
检查所有要求的投资指标是否正确存储在数据库中
"""

import os
import sys
import django
from datetime import datetime
import logging

# 添加Django项目路径
sys.path.append('/Volumes/Pickle Samsung SSD/MEM Dashboard 2/src/django_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')

# 初始化Django
django.setup()

from bea.models import BeaIndicator, BeaIndicatorConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/Volumes/Pickle Samsung SSD/MEM Dashboard 2/logs/validate_bea_table526_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BeaTable526Validator:
    """BEA Table 5.2.6投资指标数据库验证器"""

    def __init__(self):
        # 预期的投资指标配置（基于您的要求）
        self.expected_indicators = {
            'INVESTMENT_TOTAL': {
                'line_number': 4,
                'name': 'Gross Private Domestic Investment',
                'table_name': 'T50206'
            },
            'INVESTMENT_FIXED': {
                'line_number': 7,
                'name': 'Fixed Investment',
                'table_name': 'T50206'
            },
            'INVESTMENT_NONRESIDENTIAL': {
                'line_number': 10,
                'name': 'Nonresidential Investment',
                'table_name': 'T50206'
            },
            'INVESTMENT_STRUCTURES': {
                'line_number': 13,
                'name': 'Structures',
                'table_name': 'T50206'
            },
            'INVESTMENT_EQUIPMENT': {
                'line_number': 16,
                'name': 'Equipment',
                'table_name': 'T50206'
            },
            'INVESTMENT_IP': {
                'line_number': 19,
                'name': 'Intellectual Property Products',
                'table_name': 'T50206'
            },
            'INVESTMENT_RESIDENTIAL': {
                'line_number': 22,
                'name': 'Residential Investment',
                'table_name': 'T50206'
            },
            'INVESTMENT_INVENTORIES': {
                'line_number': 25,
                'name': 'Change in Private Inventories',
                'table_name': 'T50206'
            },
            'INVESTMENT_NET': {
                'line_number': 6,
                'name': 'Net Private Domestic Investment',
                'table_name': 'T50206'
            },
            'GOVT_INVESTMENT_TOTAL': {
                'line_number': 26,
                'name': 'Gross Government Investment',
                'table_name': 'T50206'
            }
        }

        self.stats = {
            'found_indicators': 0,
            'missing_indicators': 0,
            'total_records': 0,
            'latest_data_year': None
        }

    def validate_indicator(self, series_id, expected_info):
        """验证单个指标"""
        logger.info(f"\n{'='*20} 验证指标: {series_id} {'='*20}")

        # 检查配置是否存在
        try:
            config = BeaIndicatorConfig.objects.get(series_id=series_id)
            logger.info(f"✅ 配置存在: {config.name}")
            logger.info(f"   表名: {config.table_name}, 行号: {config.line_number}")
        except BeaIndicatorConfig.DoesNotExist:
            logger.warning(f"⚠️ 配置不存在: {series_id}")
            self.stats['missing_indicators'] += 1
            return False

        # 检查数据是否存在
        indicators = BeaIndicator.objects.filter(series_id=series_id)
        record_count = indicators.count()

        if record_count == 0:
            logger.error(f"❌ 无数据: {series_id}")
            self.stats['missing_indicators'] += 1
            return False

        logger.info(f"✅ 数据存在: {record_count} 条记录")
        self.stats['found_indicators'] += 1
        self.stats['total_records'] += record_count

        # 获取最新数据
        latest = indicators.order_by('-date').first()
        if latest:
            logger.info(f"📊 最新数据: {latest.value} ({latest.time_period})")
            logger.info(f"   单位: {latest.unit}")
            logger.info(f"   来源: {latest.source}")

            # 更新最新数据年份
            try:
                year = int(latest.time_period)
                if not self.stats['latest_data_year'] or year > self.stats['latest_data_year']:
                    self.stats['latest_data_year'] = year
            except:
                pass

        # 获取最早数据
        earliest = indicators.order_by('date').first()
        if earliest:
            logger.info(f"📊 最早数据: {earliest.value} ({earliest.time_period})")

        # 验证关键字段
        if latest:
            # 验证表名和行号
            if latest.table_name != expected_info['table_name']:
                logger.warning(f"⚠️ 表名不匹配: 期望 {expected_info['table_name']}, 实际 {latest.table_name}")
            if latest.line_number != str(expected_info['line_number']):
                logger.warning(f"⚠️ 行号不匹配: 期望 {expected_info['line_number']}, 实际 {latest.line_number}")

            # 验证数值合理性
            if latest.value < -1000000 or latest.value > 10000000:  # 基于投资数据合理范围
                logger.warning(f"⚠️ 数值可能异常: {latest.value}")

        return True

    def validate_all_indicators(self):
        """验证所有预期的指标"""
        logger.info(f"🚀 开始验证BEA Table 5.2.6投资指标数据库数据...")
        logger.info(f"📊 需要验证 {len(self.expected_indicators)} 个指标")

        success_count = 0

        for series_id, expected_info in self.expected_indicators.items():
            try:
                if self.validate_indicator(series_id, expected_info):
                    success_count += 1
            except Exception as e:
                logger.error(f"❌ 验证异常 {series_id}: {e}")
                self.stats['missing_indicators'] += 1

        return success_count

    def generate_summary_report(self):
        """生成验证总结报告"""
        logger.info("\n" + "="*80)
        logger.info("📊 BEA Table 5.2.6投资指标数据库验证报告")
        logger.info("="*80)

        logger.info(f"预期指标总数: {len(self.expected_indicators)}")
        logger.info(f"找到的指标数: {self.stats['found_indicators']}")
        logger.info(f"缺失的指标数: {self.stats['missing_indicators']}")
        logger.info(f"总数据记录数: {self.stats['total_records']}")
        logger.info(f"最新数据年份: {self.stats['latest_data_year'] or '未知'}")

        if self.stats['found_indicators'] > 0:
            avg_records = self.stats['total_records'] / self.stats['found_indicators']
            logger.info(f"每个指标平均记录数: {avg_records:.1f}")

        success_rate = (self.stats['found_indicators'] / len(self.expected_indicators)) * 100
        logger.info(f"数据完整率: {success_rate:.1f}%")

        # 详细列出所有指标状态
        logger.info("\n各指标详细状态:")
        for series_id, expected_info in self.expected_indicators.items():
            indicators = BeaIndicator.objects.filter(series_id=series_id)
            record_count = indicators.count()

            if record_count > 0:
                latest = indicators.order_by('-date').first()
                status = "✅ 存在"
                details = f"{record_count} 条记录 (最新: {latest.time_period})"
            else:
                status = "❌ 缺失"
                details = "无数据"

            logger.info(f"{status} {series_id}: {expected_info['name']} - {details}")

    def run(self):
        """主执行流程"""
        try:
            success_count = self.validate_all_indicators()
            self.generate_summary_report()

            if success_count == len(self.expected_indicators):
                logger.info("🎉 所有投资指标数据验证通过")
                return True
            else:
                logger.warning(f"⚠️ 部分指标数据缺失: {success_count}/{len(self.expected_indicators)}")
                return False

        except Exception as e:
            logger.error(f"💥 验证过程异常: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

def main():
    """主函数"""
    try:
        logger.info("=" * 60)
        logger.info("BEA Table 5.2.6投资指标数据库验证器启动")
        logger.info("=" * 60)

        validator = BeaTable526Validator()
        success = validator.run()

        if success:
            logger.info("✅ 数据库验证任务成功完成")
            sys.exit(0)
        else:
            logger.error("❌ 数据库验证发现问题")
            sys.exit(1)

    except Exception as e:
        logger.error(f"💥 系统异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(2)

if __name__ == "__main__":
    main()
