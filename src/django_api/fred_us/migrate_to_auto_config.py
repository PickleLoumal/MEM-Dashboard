"""
FRED US 配置数据库初始化脚本
基于现有 Series Info 数据创建自动配置
"""

import os
import sys
import django

# 添加Django项目路径
sys.path.append('/Volumes/Pickle Samsung SSD/MEM Dashboard 2/src/django_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')
django.setup()

from fred_us.models import FredUsSeriesInfo, FredUsIndicatorConfig
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def create_fred_us_configs():
    """基于现有Series Info创建自动配置"""
    
    # 获取所有现有的Series Info
    series_infos = FredUsSeriesInfo.objects.all()
    created_count = 0
    updated_count = 0
    
    logger.info(f"Found {series_infos.count()} series to process")
    
    # 为每个Series Info创建配置
    for info in series_infos:
        # 生成API端点名称
        api_endpoint = f"/{info.series_id.lower().replace('_', '-')}/"
        
        # 根据频率设置抓取频率
        fetch_freq_map = {
            'daily': 'daily',
            'weekly': 'weekly', 
            'monthly': 'daily',  # 月度数据每天检查
            'quarterly': 'weekly',  # 季度数据每周检查
            'annual': 'monthly'  # 年度数据每月检查
        }
        frequency_str = info.frequency.lower() if info.frequency else 'monthly'
        fetch_frequency = fetch_freq_map.get(frequency_str, 'daily')
        
        # 根据类别设置优先级
        priority_map = {
            'monetary': 10,  # 货币政策最高优先级
            'employment': 20,  # 就业次之
            'prices': 30,  # 价格指标
            'fiscal': 40,  # 财政指标
            'housing': 50,  # 房地产指标
            'trade': 60,  # 贸易指标
        }
        category_str = info.category if info.category else 'other'
        priority = priority_map.get(category_str, 999)
        
        # 设置描述
        description = f"{info.title} - {info.units or 'Unknown Units'}"
        if info.seasonal_adjustment:
            description += f" ({info.seasonal_adjustment})"
        
        config_data = {
            'series_id': info.series_id,
            'name': info.title,
            'description': description,
            'indicator_type': info.series_id.lower(),
            'units': info.units or 'Unknown',
            'frequency': info.frequency.capitalize() if info.frequency else 'Monthly',
            'category': category_str,
            'api_endpoint': api_endpoint,
            'fallback_value': None,  # 将在后续添加基于历史数据的默认值
            'priority': priority,
            'is_active': True,
            'auto_fetch': True,
            'fetch_frequency': fetch_frequency,
            'created_by': 'system_migration',
            'updated_by': 'system_migration',
            'additional_config': {
                'seasonal_adjustment': info.seasonal_adjustment,
                'data_source': 'FRED API',
                'original_notes': info.notes,
                'data_limit': 100,  # 默认获取最近100条数据
                'migration_date': timezone.now().isoformat()
            }
        }
        
        # 创建或更新配置
        _, created = FredUsIndicatorConfig.objects.update_or_create(
            series_id=info.series_id,
            defaults=config_data
        )
        
        if created:
            created_count += 1
            logger.info(f"Created config for {info.series_id}: {info.title}")
        else:
            updated_count += 1
            logger.info(f"Updated config for {info.series_id}: {info.title}")
    
    logger.info("Migration Summary:")
    logger.info(f"- Created: {created_count} new configurations")
    logger.info(f"- Updated: {updated_count} existing configurations")
    logger.info(f"- Total: {created_count + updated_count} configurations processed")
    
    # 验证配置
    total_configs = FredUsIndicatorConfig.objects.count()
    active_configs = FredUsIndicatorConfig.objects.filter(is_active=True).count()
    auto_fetch_configs = FredUsIndicatorConfig.objects.filter(auto_fetch=True).count()
    
    logger.info("Configuration Verification:")
    logger.info(f"- Total configurations: {total_configs}")
    logger.info(f"- Active configurations: {active_configs}")
    logger.info(f"- Auto-fetch enabled: {auto_fetch_configs}")
    
    # 按类别统计
    logger.info("By Category:")
    categories = FredUsIndicatorConfig.objects.values_list('category', flat=True).distinct()
    for category in categories:
        count = FredUsIndicatorConfig.objects.filter(category=category).count()
        logger.info(f"- {category}: {count} indicators")
    
    return created_count, updated_count


def validate_migration():
    """验证迁移结果"""
    logger.info("Validation Results:")
    
    # 检查是否所有Series Info都有对应的配置
    series_infos = FredUsSeriesInfo.objects.all()
    configs = FredUsIndicatorConfig.objects.all()
    
    series_ids = set(series_infos.values_list('series_id', flat=True))
    config_ids = set(configs.values_list('series_id', flat=True))
    
    missing_configs = series_ids - config_ids
    extra_configs = config_ids - series_ids
    
    if missing_configs:
        logger.warning(f"Missing configurations for: {missing_configs}")
    else:
        logger.info("All Series Info have corresponding configurations")
    
    if extra_configs:
        logger.info(f"Extra configurations (no Series Info): {extra_configs}")
    
    # 检查自动抓取配置
    auto_fetch_count = configs.filter(auto_fetch=True, is_active=True).count()
    logger.info(f"{auto_fetch_count} indicators configured for automatic fetching")
    
    return len(missing_configs) == 0


if __name__ == "__main__":
    # Configure console logging for CLI execution
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    logger.info("Starting FRED US Configuration Migration")
    logger.info("Based on BEA system patterns")
    logger.info("-" * 50)
    
    try:
        created, updated = create_fred_us_configs()
        
        logger.info("=" * 50)
        validation_passed = validate_migration()
        
        if validation_passed:
            logger.info("Migration completed successfully!")
            logger.info("All FRED US Series Info converted to auto-fetch configurations")
        else:
            logger.warning("Migration completed with warnings")
            logger.warning("Please review the missing configurations")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
