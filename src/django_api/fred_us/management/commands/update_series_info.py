"""
Django管理命令: 更新缺失的FRED US Series Info
从FRED API获取缺失的系列信息并更新数据库
"""

import time
from typing import List, Dict, Any
from django.core.management.base import BaseCommand, CommandError
from fred_us.models import FredUsIndicator, FredUsSeriesInfo
from fred_us.data_fetcher import UsFredDataFetcher


class Command(BaseCommand):
    help = '更新缺失的FRED US Series Info'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示缺失的指标，不实际更新'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='限制处理的指标数量'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='API调用间隔延迟（秒）'
        )

    def handle(self, *args, **options):
        """处理命令执行"""
        try:
            self.stdout.write(
                self.style.HTTP_INFO("FRED US Series Info 数据库整理工具")
            )
            self.stdout.write("=" * 60)
            
            # 获取缺失的series_id
            missing_series = self._get_missing_series_ids()
            
            if not missing_series:
                self.stdout.write(
                    self.style.SUCCESS("✓ 所有指标的Series Info已完整，无需更新!")
                )
                return
            
            # 应用限制
            if options['limit']:
                missing_series = missing_series[:options['limit']]
            
            self.stdout.write(f"发现 {len(missing_series)} 个缺失的Series Info:")
            for i, series_id in enumerate(missing_series[:10], 1):
                self.stdout.write(f"  {i:2d}. {series_id}")
            if len(missing_series) > 10:
                self.stdout.write(f"  ... 以及其他 {len(missing_series) - 10} 个")
            
            # 如果是dry-run，只显示信息
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING("\n这是预览模式，没有实际更新数据库。")
                )
                return
            
            # 执行批量更新
            results = self._fetch_and_save_series_info(
                missing_series, 
                delay=options['delay']
            )
            
            # 验证结果
            self._verify_update()
            
            self.stdout.write(
                self.style.SUCCESS("\n数据库整理完成!")
            )
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n操作被用户中断')
            )
        except Exception as e:
            raise CommandError(f'命令执行失败: {e}')

    def _get_missing_series_ids(self) -> List[str]:
        """获取缺失Series Info的series_id列表"""
        indicators_series = set(
            FredUsIndicator.objects.values_list('series_id', flat=True).distinct()
        )
        series_info_series = set(
            FredUsSeriesInfo.objects.values_list('series_id', flat=True)
        )
        
        missing_series = indicators_series - series_info_series
        return sorted(missing_series)

    def _fetch_and_save_series_info(self, series_ids: List[str], delay: float = 1.0) -> Dict[str, Any]:
        """批量获取并保存系列信息"""
        results = {
            'total': len(series_ids),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # 创建数据获取器
            fetcher = UsFredDataFetcher()
            
            self.stdout.write(f"\n开始获取 {len(series_ids)} 个缺失的Series Info...")
            self.stdout.write("=" * 60)
            
            for i, series_id in enumerate(series_ids, 1):
                try:
                    self.stdout.write(
                        f"[{i:2d}/{len(series_ids)}] 获取 {series_id} 的系列信息...",
                        ending=''
                    )
                    
                    # 获取系列信息
                    series_info = fetcher.get_series_info(series_id)
                    
                    if series_info:
                        # 保存到数据库
                        success = fetcher.save_series_info(series_id, series_info)
                        
                        if success:
                            results['successful'] += 1
                            title = series_info.get('title', 'N/A')
                            # 截断长标题
                            if len(title) > 50:
                                title = title[:47] + "..."
                            self.stdout.write(
                                self.style.SUCCESS(f" ✓ {title}")
                            )
                        else:
                            results['failed'] += 1
                            error_msg = f"保存失败: {series_id}"
                            results['errors'].append(error_msg)
                            self.stdout.write(
                                self.style.ERROR(f" ✗ 保存失败")
                            )
                    else:
                        results['failed'] += 1
                        error_msg = f"API未返回数据: {series_id}"
                        results['errors'].append(error_msg)
                        self.stdout.write(
                            self.style.ERROR(f" ✗ API无数据")
                        )
                    
                    # 添加延迟避免API限制
                    if i < len(series_ids):  # 最后一个不需要延迟
                        time.sleep(delay)
                        
                except Exception as e:
                    results['failed'] += 1
                    error_msg = f"处理 {series_id} 时出错: {str(e)}"
                    results['errors'].append(error_msg)
                    self.stdout.write(
                        self.style.ERROR(f" ✗ 错误: {str(e)}")
                    )
                    continue
            
            self.stdout.write("=" * 60)
            self.stdout.write(
                self.style.HTTP_INFO(f"批量更新完成!")
            )
            self.stdout.write(f"总计: {results['total']} 个指标")
            self.stdout.write(
                self.style.SUCCESS(f"成功: {results['successful']} 个")
            )
            if results['failed'] > 0:
                self.stdout.write(
                    self.style.ERROR(f"失败: {results['failed']} 个")
                )
            
            if results['errors'] and results['failed'] <= 5:  # 只在失败数量较少时显示详情
                self.stdout.write(f"\n错误详情:")
                for error in results['errors']:
                    self.stdout.write(f"  • {error}")
            
            return results
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"批量更新过程中发生错误: {e}")
            )
            return results

    def _verify_update(self) -> None:
        """验证更新结果"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.HTTP_INFO("验证更新结果:")
        )
        
        indicators_count = FredUsIndicator.objects.values('series_id').distinct().count()
        series_info_count = FredUsSeriesInfo.objects.count()
        
        self.stdout.write(f"Indicators表中的唯一series_id数量: {indicators_count}")
        self.stdout.write(f"Series Info表中的记录数量: {series_info_count}")
        self.stdout.write(f"缺失的Series Info数量: {indicators_count - series_info_count}")
        
        if indicators_count == series_info_count:
            self.stdout.write(
                self.style.SUCCESS("✓ 所有指标的Series Info已完整!")
            )
        else:
            missing_series = self._get_missing_series_ids()
            self.stdout.write(
                self.style.WARNING(f"✗ 仍有 {len(missing_series)} 个指标缺失Series Info:")
            )
            for series_id in missing_series[:5]:  # 只显示前5个
                self.stdout.write(f"  • {series_id}")
            if len(missing_series) > 5:
                self.stdout.write(f"  ... 以及其他 {len(missing_series) - 5} 个")




