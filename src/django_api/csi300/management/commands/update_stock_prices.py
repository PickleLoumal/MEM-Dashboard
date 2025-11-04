"""
Django management command to update stock prices daily
Usage: python manage.py update_stock_prices
"""

import yfinance as yf
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from csi300.models import CSI300Company
import logging

logger = logging.getLogger(__name__)

# Note: yfinance 0.2.36+ handles sessions internally with curl_cffi
# No need to create custom session - let yfinance handle it


class Command(BaseCommand):
    help = 'Update stock prices (open, previous close, 52w high/low, last trade date) for all CSI300 companies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbol',
            type=str,
            help='Update specific symbol only (e.g., 000002.SZ)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without saving to database',
        )

    def handle(self, *args, **options):
        symbol_filter = options.get('symbol')
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be saved'))
        
        # Get companies to update
        if symbol_filter:
            companies = CSI300Company.objects.filter(ticker=symbol_filter)
            if not companies.exists():
                self.stdout.write(self.style.ERROR(f'❌ Symbol {symbol_filter} not found'))
                return
        else:
            companies = CSI300Company.objects.all()
        
        total = companies.count()
        updated = 0
        failed = 0
        
        self.stdout.write(self.style.SUCCESS(f'📊 Updating {total} companies...'))
        
        for company in companies:
            try:
                if not company.ticker:
                    self.stdout.write(self.style.WARNING(f'⚠️  Skipping {company.name}: No ticker'))
                    continue
                
                # Fetch data from yfinance
                stock = yf.Ticker(company.ticker)
                info = stock.info
                
                # Get historical data for previous close
                hist = stock.history(period='5d')
                
                if hist.empty:
                    self.stdout.write(self.style.WARNING(f'⚠️  {company.ticker}: No historical data'))
                    failed += 1
                    continue
                
                # Extract data
                last_close = float(hist['Close'].iloc[-1]) if len(hist) > 0 else None
                previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else last_close
                open_price = float(hist['Open'].iloc[-1]) if len(hist) > 0 else None
                
                # Get 52-week high/low
                fifty_two_week_high = info.get('fiftyTwoWeekHigh')
                fifty_two_week_low = info.get('fiftyTwoWeekLow')
                
                # Get last trade date
                last_trade_date = hist.index[-1].date() if len(hist) > 0 else None
                
                # Prepare update data
                update_data = {}
                
                if open_price is not None:
                    update_data['price_local_currency'] = open_price
                
                if previous_close is not None:
                    update_data['previous_close'] = previous_close
                
                if fifty_two_week_high is not None:
                    update_data['price_52w_high'] = fifty_two_week_high
                
                if fifty_two_week_low is not None:
                    update_data['price_52w_low'] = fifty_two_week_low
                
                if last_trade_date is not None:
                    update_data['last_trade_date'] = last_trade_date
                
                # Display update info
                open_str = f'{open_price:.2f}' if open_price is not None else 'N/A'
                prev_close_str = f'{previous_close:.2f}' if previous_close is not None else 'N/A'
                high_str = f'{fifty_two_week_high:.2f}' if fifty_two_week_high is not None else 'N/A'
                low_str = f'{fifty_two_week_low:.2f}' if fifty_two_week_low is not None else 'N/A'
                
                self.stdout.write(
                    f'✅ {company.ticker} ({company.name[:30]}): '
                    f'Open={open_str}, '
                    f'Prev Close={prev_close_str}, '
                    f'52W H/L={high_str}/{low_str}, '
                    f'Last Trade={last_trade_date}'
                )
                
                # Save to database (unless dry run)
                if not dry_run and update_data:
                    for field, value in update_data.items():
                        setattr(company, field, value)
                    company.save(update_fields=list(update_data.keys()) + ['updated_at'])
                
                updated += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ {company.ticker}: {str(e)}'))
                logger.error(f'Failed to update {company.ticker}: {e}', exc_info=True)
                failed += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n📈 Update Summary:'))
        self.stdout.write(f'   Total: {total}')
        self.stdout.write(self.style.SUCCESS(f'   ✅ Updated: {updated}'))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f'   ❌ Failed: {failed}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN COMPLETE - No changes were saved'))

