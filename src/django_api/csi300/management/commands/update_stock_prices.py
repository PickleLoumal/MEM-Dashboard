"""
Django management command to update stock prices daily
Usage:
    python manage.py update_stock_prices
    python manage.py update_stock_prices --exchange HKEX
    python manage.py update_stock_prices --symbol 0700.HK
"""

import logging
from datetime import UTC, datetime, timedelta

import pandas as pd
from csi300.models import Company
from django.core.management.base import BaseCommand
from stocks.akshare_client import get_daily_data, normalize_symbol

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update stock prices (open, previous close, 52w high/low, last trade date) for all companies"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            help="Update specific symbol only (e.g., 000002.SZ, 0700.HK)",
        )
        parser.add_argument(
            "--exchange",
            type=str,
            choices=["SSE", "SZSE", "HKEX"],
            default=None,
            help="Filter by exchange (SSE, SZSE, HKEX)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without saving to database",
        )

    @staticmethod
    def fetch_daily_bars(symbol: str, days: int = 460) -> pd.DataFrame:
        """
        Fetch recent daily bars from AkShare for the specified security.
        Defaults to ~18 months of data to compute 52-week metrics.
        """
        end_time = datetime.now(tz=UTC)
        start_time = end_time - timedelta(days=days)

        df = get_daily_data(symbol, start_time, end_time)
        if df.empty:
            return df

        df = df.rename(
            columns={
                "Date": "trade_date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "vol",
            }
        )

        df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce")
        df = df.dropna(subset=["trade_date"])
        df = df.sort_values("trade_date")
        df["pre_close"] = df["close"].shift(1)

        return df

    def handle(self, *args, **options):
        symbol_filter = options.get("symbol")
        exchange_filter = options.get("exchange")
        dry_run = options.get("dry_run", False)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be saved"))

        # Get companies to update
        queryset = Company.objects.all()

        if symbol_filter:
            queryset = queryset.filter(ticker=symbol_filter)
            if not queryset.exists():
                self.stdout.write(self.style.ERROR(f"Symbol {symbol_filter} not found"))
                return

        if exchange_filter:
            queryset = queryset.filter(exchange=exchange_filter)
            self.stdout.write(f"Filtering by exchange: {exchange_filter}")

        companies = queryset
        total = companies.count()
        updated = 0
        failed = 0

        self.stdout.write(self.style.SUCCESS(f"Updating {total} companies..."))

        for company in companies:
            try:
                if not company.ticker:
                    self.stdout.write(self.style.WARNING(f"Skipping {company.name}: No ticker"))
                    continue

                if not normalize_symbol(company.ticker):
                    self.stdout.write(
                        self.style.ERROR(f"{company.ticker}: Unsupported ticker format for AkShare")
                    )
                    failed += 1
                    continue

                hist = self.fetch_daily_bars(company.ticker)
                if hist.empty:
                    self.stdout.write(
                        self.style.WARNING(f"{company.ticker}: No AkShare data returned")
                    )
                    failed += 1
                    continue

                last_row = hist.iloc[-1]
                open_price = float(last_row["open"])
                last_close = float(last_row["close"])

                if pd.notna(last_row.get("pre_close")):
                    previous_close = float(last_row["pre_close"])
                elif len(hist) > 1:
                    previous_close = float(hist["close"].iloc[-2])
                else:
                    previous_close = last_close

                recent_window = hist.tail(260)
                if recent_window.empty:
                    recent_window = hist

                fifty_two_week_high = (
                    float(recent_window["high"].max()) if not recent_window.empty else None
                )
                fifty_two_week_low = (
                    float(recent_window["low"].min()) if not recent_window.empty else None
                )

                if pd.isna(fifty_two_week_high):
                    fifty_two_week_high = None
                if pd.isna(fifty_two_week_low):
                    fifty_two_week_low = None

                if pd.isna(open_price):
                    open_price = None
                if pd.isna(previous_close):
                    previous_close = None
                if pd.isna(last_close):
                    last_close = None

                last_trade_date = last_row["trade_date"].date()

                # Prepare update data
                update_data = {}

                if open_price is not None:
                    update_data["price_local_currency"] = open_price

                if previous_close is not None:
                    update_data["previous_close"] = previous_close

                if fifty_two_week_high is not None:
                    update_data["price_52w_high"] = fifty_two_week_high

                if fifty_two_week_low is not None:
                    update_data["price_52w_low"] = fifty_two_week_low

                if last_trade_date is not None:
                    update_data["last_trade_date"] = last_trade_date

                # Display update info
                open_str = f"{open_price:.2f}" if open_price is not None else "N/A"
                prev_close_str = f"{previous_close:.2f}" if previous_close is not None else "N/A"
                high_str = (
                    f"{fifty_two_week_high:.2f}" if fifty_two_week_high is not None else "N/A"
                )
                low_str = f"{fifty_two_week_low:.2f}" if fifty_two_week_low is not None else "N/A"

                self.stdout.write(
                    f"{company.ticker} ({company.name[:30]}) [{company.exchange}]: "
                    f"Open={open_str}, "
                    f"Prev Close={prev_close_str}, "
                    f"52W H/L={high_str}/{low_str}, "
                    f"Last Trade={last_trade_date}"
                )

                # Save to database (unless dry run)
                if not dry_run and update_data:
                    for field, value in update_data.items():
                        setattr(company, field, value)
                    company.save(update_fields=[*list(update_data.keys()), "updated_at"])

                updated += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{company.ticker}: {e!s}"))
                logger.exception("Failed to update %s", company.ticker)
                failed += 1

        # Summary
        self.stdout.write(self.style.SUCCESS("\nUpdate Summary:"))
        self.stdout.write(f"   Total: {total}")
        self.stdout.write(self.style.SUCCESS(f"   Updated: {updated}"))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f"   Failed: {failed}"))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN COMPLETE - No changes were saved"))
