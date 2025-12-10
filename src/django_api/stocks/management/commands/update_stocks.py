import time

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from stocks.services import StockDataService


class Command(BaseCommand):
    """股票数据更新管理命令"""

    help = "Update stock data using AkShare"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbols",
            nargs="*",
            type=str,
            help="Specific stock symbols to update (e.g., AAPL MSFT GOOGL)",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=60,
            help="Update interval in seconds (default: 60)",
        )
        parser.add_argument(
            "--duration",
            type=int,
            default=300,
            help="Total duration to run updates in seconds (default: 300)",
        )
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run update once instead of continuously",
        )
        parser.add_argument(
            "--initialize",
            action="store_true",
            help="Initialize stock symbols before updating",
        )

    def handle(self, *args, **options):
        """执行命令的主要逻辑"""
        self.stdout.write(self.style.SUCCESS("🧪 Starting AkShare Stock Data Update"))

        # 初始化服务
        service = StockDataService()

        # 初始化股票代码（如果指定）
        if options["initialize"]:
            self.stdout.write("📋 Initializing stock symbols...")
            initialized = service.initialize_stock_symbols()
            self.stdout.write(self.style.SUCCESS(f"✅ Initialized {initialized} stock symbols"))

        # 获取要更新的股票列表
        symbols = options["symbols"]
        if not symbols:
            # 从 CSI300 数据库获取股票代码，或使用默认列表
            csi300_tickers = service.get_csi300_tickers(limit=20)
            if csi300_tickers:
                symbols = csi300_tickers
                self.stdout.write(f"📊 Using CSI300 tickers: {len(symbols)} stocks")
            else:
                symbols = service.default_symbols
                self.stdout.write(f"📊 Using default symbols: {', '.join(symbols)}")

        self.stdout.write(f"📊 Monitoring symbols: {', '.join(symbols)}")

        # 单次更新模式
        if options["once"]:
            self.stdout.write("🔄 Running single update...")
            result = service.update_all_stocks(symbols)

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Update completed: {result['successful']} successful, "
                    f"{result['failed']} failed, {result['updated_count']} records updated"
                )
            )

            # 显示错误（如果有）
            if result["errors"]:
                self.stdout.write(self.style.WARNING("❌ Errors encountered:"))
                for error in result["errors"]:
                    self.stdout.write(f"  - {error['symbol']}: {error['error']}")

            return

        # 持续更新模式
        interval = options["interval"]
        duration = options["duration"]

        self.stdout.write(
            f"🚀 Starting continuous updates for {duration} seconds (interval: {interval}s)"
        )

        start_time = time.time()
        end_time = start_time + duration

        try:
            while time.time() < end_time:
                loop_start = time.time()

                # 执行更新
                result = service.update_all_stocks(symbols)

                # 显示更新结果
                self.stdout.write(
                    f"📈 Update at {timezone.now().strftime('%H:%M:%S')}: "
                    f"{result['successful']}/{result['total_symbols']} successful, "
                    f"{result['updated_count']} records"
                )

                # 显示错误（如果有）
                if result["errors"]:
                    for error in result["errors"][:3]:  # 只显示前3个错误
                        self.stdout.write(
                            self.style.WARNING(f"  ❌ {error['symbol']}: {error['error']}")
                        )

                # 计算下次更新时间
                loop_time = time.time() - loop_start
                sleep_time = max(0, interval - loop_time)

                if sleep_time > 0:
                    self.stdout.write(f"⏱️  Waiting {sleep_time:.1f}s for next update...")
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n🛑 Update stopped by user"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Unexpected error: {e}"))
            raise CommandError(f"Update failed: {e}") from e

        self.stdout.write(self.style.SUCCESS("✅ Stock data updates completed"))
