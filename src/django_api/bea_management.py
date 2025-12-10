#!/usr/bin/env python3
"""
BEA动态指标管理脚本
演示如何使用动态配置系统管理BEA指标
"""

import os
import sys
import django
from pathlib import Path

# 添加Django项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from bea.models import BeaIndicatorConfig
from bea.dynamic_config import DynamicBeaConfigManager
import logging

# Configure console logging for CLI
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def create_sample_configs():
    """创建示例BEA指标配置"""
    
    sample_configs = [
        {
            'series_id': 'MOTOR_VEHICLES',
            'name': 'Motor Vehicles and Parts',
            'category': 'consumer_spending',
            'description': 'Personal consumption expenditures on motor vehicles and parts',
            'api_endpoint': '/motor_vehicles/',
            'table_name': 'Table 2.4.5U',
            'line_description': 'Motor vehicles and parts',
            'line_number': 15,
            'units': 'Billions of chained 2012 dollars',
            'frequency': 'Q',
            'auto_fetch': True,
            'is_active': True,
            'priority': 10,
            'fallback_value': 750.144,
            'dataset_name': 'NIPA',
            'additional_config': {
                'seasonally_adjusted': True,
                'data_source': 'BEA NIPA Tables'
            }
        },
        {
            'series_id': 'RECREATIONAL_GOODS',
            'name': 'Recreational Goods and Vehicles',
            'category': 'consumer_spending',
            'description': 'Personal consumption expenditures on recreational goods and vehicles',
            'api_endpoint': '/recreational_goods/',
            'table_name': 'Table 2.4.5U',
            'line_description': 'Recreational goods and vehicles',
            'line_number': 34,
            'units': 'Billions of chained 2012 dollars',
            'frequency': 'Q',
            'auto_fetch': True,
            'is_active': True,
            'priority': 15,
            'fallback_value': 677.1,
            'dataset_name': 'NIPA',
            'additional_config': {
                'seasonally_adjusted': True,
                'data_source': 'BEA NIPA Tables'
            }
        },
        {
            'series_id': 'HOUSING_UTILITIES',
            'name': 'Housing and Utilities',
            'category': 'consumer_spending',
            'description': 'Personal consumption expenditures on housing and utilities',
            'api_endpoint': '/housing_utilities/',
            'table_name': 'Table 2.4.5U',
            'line_description': 'Housing and utilities',
            'line_number': 4,
            'units': 'Billions of chained 2012 dollars',
            'frequency': 'Q',
            'auto_fetch': True,
            'is_active': True,
            'priority': 5,
            'fallback_value': 2451.8,
            'dataset_name': 'NIPA',
            'additional_config': {
                'seasonally_adjusted': True,
                'data_source': 'BEA NIPA Tables'
            }
        },
        {
            'series_id': 'FOOD_BEVERAGES',
            'name': 'Food and Beverages',
            'category': 'consumer_spending',
            'description': 'Personal consumption expenditures on food and beverages',
            'api_endpoint': '/food_beverages/',
            'table_name': 'Table 2.4.5U',
            'line_description': 'Food and beverages purchased for off-premises consumption',
            'line_number': 5,
            'units': 'Billions of chained 2012 dollars',
            'frequency': 'Q',
            'auto_fetch': True,
            'is_active': True,
            'priority': 8,
            'fallback_value': 1987.6,
            'dataset_name': 'NIPA',
            'additional_config': {
                'seasonally_adjusted': True,
                'data_source': 'BEA NIPA Tables'
            }
        },
        {
            'series_id': 'HEALTHCARE',
            'name': 'Health Care',
            'category': 'consumer_spending',
            'description': 'Personal consumption expenditures on health care',
            'api_endpoint': '/healthcare/',
            'table_name': 'Table 2.4.5U',
            'line_description': 'Health care',
            'line_number': 18,
            'units': 'Billions of chained 2012 dollars',
            'frequency': 'Q',
            'auto_fetch': True,
            'is_active': True,
            'priority': 12,
            'fallback_value': 2890.4,
            'dataset_name': 'NIPA',
            'additional_config': {
                'seasonally_adjusted': True,
                'data_source': 'BEA NIPA Tables'
            }
        }
    ]
    
    created_count = 0
    for config_data in sample_configs:
        try:
            # 检查是否已存在
            existing = BeaIndicatorConfig.objects.filter(series_id=config_data['series_id']).first()
            if existing:
                logger.info(f"配置已存在: {config_data['series_id']} - 跳过")
                continue
            
            # 创建新配置
            config = BeaIndicatorConfig.objects.create(**config_data)
            logger.info(f"创建配置: {config.series_id} - {config.name}")
            created_count += 1
            
        except Exception as e:
            logger.error(f"创建配置失败 {config_data['series_id']}: {e}")
    
    logger.info(f"总共创建 {created_count} 个新配置")
    
    # 清除缓存
    DynamicBeaConfigManager.clear_all_cache()
    logger.info("缓存已清除")


def list_all_configs():
    """列出所有配置"""
    logger.info("=== 所有BEA指标配置 ===")
    
    configs = BeaIndicatorConfig.objects.all().order_by('priority', 'series_id')
    
    logger.info(f"{'Series ID':<20} {'Name':<30} {'Category':<20} {'Active':<8} {'Priority':<8}")
    logger.info("-" * 90)
    
    for config in configs:
        status_str = "Y" if config.is_active else "N"
        logger.info(f"{config.series_id:<20} {config.name[:28]:<30} {config.category:<20} {status_str:<8} {config.priority or 'N/A':<8}")
    
    logger.info(f"总计: {configs.count()} 个配置")


def test_dynamic_system():
    """测试动态配置系统"""
    logger.info("=== 测试动态配置系统 ===")
    
    # 测试配置管理器
    try:
        all_indicators = DynamicBeaConfigManager.get_all_indicators()
        logger.info(f"获取所有指标配置: {len(all_indicators)} 个")
        
        auto_fetch = DynamicBeaConfigManager.get_auto_fetch_indicators()
        logger.info(f"获取自动抓取配置: {len(auto_fetch)} 个")
        
        # 显示前3个配置
        logger.info("前3个激活的配置:")
        for i, (series_id, config) in enumerate(list(all_indicators.items())[:3]):
            logger.info(f"  {i+1}. {series_id}: {config['name']}")
            logger.info(f"     端点: {config['api_endpoint']}")
            logger.info(f"     分类: {config['category']}")
        
        logger.info("动态配置系统工作正常")
        
    except Exception as e:
        logger.error(f"动态配置系统测试失败: {e}")


def show_api_endpoints():
    """显示所有可用的API端点"""
    logger.info("=== 可用API端点 ===")
    
    try:
        all_configs = DynamicBeaConfigManager.get_all_indicators()
        
        logger.info("1. 管理端点:")
        management_endpoints = [
            "/api/bea/",
            "/api/bea/all_indicators/",
            "/api/bea/stats/",
            "/api/bea/api/configs/",
            "/api/bea/api/configs/active/",
            "/api/bea/api/configs/categories/",
            "/api/bea/health/"
        ]
        
        for endpoint in management_endpoints:
            logger.info(f"   {endpoint}")
        
        logger.info("2. 动态指标端点:")
        for series_id, config in all_configs.items():
            endpoint = f"/api/bea/indicator/{series_id}/"
            logger.info(f"   {endpoint} - {config['name']}")
        
        logger.info("3. 兼容性端点:")
        legacy_endpoints = [
            "/api/bea/indicators/",
            "/api/bea/indicators/motor_vehicles/",
            "/api/bea/indicators/recreational_goods/"
        ]
        
        for endpoint in legacy_endpoints:
            logger.info(f"   {endpoint}")
        
        logger.info(f"总计: {len(management_endpoints) + len(all_configs) + len(legacy_endpoints)} 个端点")
        
    except Exception as e:
        logger.error(f"获取API端点失败: {e}")


def main():
    """主函数"""
    logger.info("BEA动态指标管理系统")
    logger.info("=" * 50)
    
    while True:
        logger.info("\n选择操作:")
        logger.info("1. 创建示例配置")
        logger.info("2. 列出所有配置")
        logger.info("3. 测试动态系统")
        logger.info("4. 显示API端点")
        logger.info("5. 退出")
        
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == '1':
            create_sample_configs()
        elif choice == '2':
            list_all_configs()
        elif choice == '3':
            test_dynamic_system()
        elif choice == '4':
            show_api_endpoints()
        elif choice == '5':
            logger.info("退出")
            break
        else:
            logger.warning("无效选择，请重试")


if __name__ == '__main__':
    main()
