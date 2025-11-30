"""
Django management command to import Investment Summary from CSV
Usage: python manage.py import_investment_summary /path/to/output.csv
"""

import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from csi300.models import CSI300Company, CSI300InvestmentSummary
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import Investment Summary data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file to import',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without saving to database',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing records instead of skipping',
        )

    @staticmethod
    def parse_price(price_str: str) -> Decimal:
        """Parse price string like 'None 157.20' or '157.20' to Decimal"""
        if not price_str:
            return Decimal('0')
        
        # Remove 'None ' prefix if present
        cleaned = re.sub(r'^None\s*', '', str(price_str).strip())
        
        # Extract numeric value
        match = re.search(r'[\d.]+', cleaned)
        if match:
            try:
                return Decimal(match.group())
            except InvalidOperation:
                return Decimal('0')
        return Decimal('0')

    @staticmethod
    def parse_date(date_str: str) -> datetime.date:
        """Parse date string to date object"""
        if not date_str:
            return datetime.now().date()
        
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(date_str.strip(), '%m/%d/%Y').date()
            except ValueError:
                return datetime.now().date()

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options.get('dry_run', False)
        update_existing = options.get('update', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be saved'))

        # CSV column to model field mapping
        field_mapping = {
            'Date': 'report_date',
            'Company': '_company_name',  # Special handling
            'Stock Price': 'stock_price_previous_close',
            'Market Cap': 'market_cap_display',
            'Recommended Action': 'recommended_action',
            'Industry': '_industry',  # For company lookup/update
            'Business Overview': 'business_overview',
            'Business Performance': 'business_performance',
            'Industry Context': 'industry_context',
            'Financial Stability': 'financial_stability',
            'Key Financials': 'key_financials_valuation',
            'Big Trends': 'big_trends_events',
            'Customer Segments': 'customer_segments',
            'Competitive Landscape': 'competitive_landscape',
            'Risks and Anomalies': 'risks_anomalies',
            'Forecast Outlook': 'forecast_outlook',
            'Investment Firms': 'investment_firms_views',
            'Industry Ratio': 'industry_ratio_analysis',
            'Recommended Action Details': 'recommended_action_detail',
            'Key Takeaways': 'key_takeaways',
        }

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                total = 0
                created = 0
                updated = 0
                skipped = 0
                failed = 0

                for row in reader:
                    total += 1
                    company_name = row.get('Company', '').strip()
                    
                    if not company_name:
                        self.stdout.write(self.style.WARNING(f'⚠️  Row {total}: Empty company name, skipping'))
                        skipped += 1
                        continue

                    try:
                        # Try to find existing company by name
                        company = CSI300Company.objects.filter(name__iexact=company_name).first()
                        
                        if not company:
                            # Try partial match
                            company = CSI300Company.objects.filter(name__icontains=company_name).first()
                        
                        if not company:
                            # Create new company
                            if not dry_run:
                                company = CSI300Company.objects.create(
                                    name=company_name,
                                    industry=row.get('Industry', '')[:500] if row.get('Industry') else None,
                                )
                                self.stdout.write(self.style.SUCCESS(f'   📝 Created company: {company_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'   📝 Would create company: {company_name}'))
                                skipped += 1
                                continue

                        # Prepare summary data
                        summary_data = {
                            'report_date': self.parse_date(row.get('Date', '')),
                            'stock_price_previous_close': self.parse_price(row.get('Stock Price', '')),
                            'market_cap_display': row.get('Market Cap', '')[:200] if row.get('Market Cap') else '',
                            'recommended_action': row.get('Recommended Action', '')[:50] if row.get('Recommended Action') else '',
                            'recommended_action_detail': row.get('Recommended Action Details', '') or '',
                            'business_overview': row.get('Business Overview', '') or '',
                            'business_performance': row.get('Business Performance', '') or '',
                            'industry_context': row.get('Industry Context', '') or '',
                            'financial_stability': row.get('Financial Stability', '') or '',
                            'key_financials_valuation': row.get('Key Financials', '') or '',
                            'big_trends_events': row.get('Big Trends', '') or '',
                            'customer_segments': row.get('Customer Segments', '') or '',
                            'competitive_landscape': row.get('Competitive Landscape', '') or '',
                            'risks_anomalies': row.get('Risks and Anomalies', '') or '',
                            'forecast_outlook': row.get('Forecast Outlook', '') or '',
                            'investment_firms_views': row.get('Investment Firms', '') or '',
                            'industry_ratio_analysis': row.get('Industry Ratio', '') or '',
                            'key_takeaways': row.get('Key Takeaways', '') or '',
                        }

                        # Check if summary already exists
                        existing_summary = CSI300InvestmentSummary.objects.filter(company=company).first()

                        if existing_summary:
                            if update_existing:
                                if not dry_run:
                                    for field, value in summary_data.items():
                                        setattr(existing_summary, field, value)
                                    existing_summary.save()
                                    updated += 1
                                    self.stdout.write(f'✅ Updated: {company_name}')
                                else:
                                    self.stdout.write(f'🔄 Would update: {company_name}')
                                    updated += 1
                            else:
                                self.stdout.write(self.style.WARNING(f'⏭️  Skipped (exists): {company_name}'))
                                skipped += 1
                        else:
                            if not dry_run:
                                CSI300InvestmentSummary.objects.create(
                                    company=company,
                                    **summary_data
                                )
                                created += 1
                                self.stdout.write(self.style.SUCCESS(f'✅ Created: {company_name}'))
                            else:
                                self.stdout.write(f'📝 Would create: {company_name}')
                                created += 1

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'❌ Row {total} ({company_name}): {str(e)}'))
                        logger.error(f'Failed to import {company_name}: {e}', exc_info=True)
                        failed += 1

                # Summary
                self.stdout.write(self.style.SUCCESS(f'\n📊 Import Summary:'))
                self.stdout.write(f'   Total rows: {total}')
                self.stdout.write(self.style.SUCCESS(f'   ✅ Created: {created}'))
                self.stdout.write(self.style.SUCCESS(f'   🔄 Updated: {updated}'))
                self.stdout.write(self.style.WARNING(f'   ⏭️  Skipped: {skipped}'))
                if failed > 0:
                    self.stdout.write(self.style.ERROR(f'   ❌ Failed: {failed}'))

                if dry_run:
                    self.stdout.write(self.style.WARNING('\n🔍 DRY RUN COMPLETE - No changes were saved'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error reading CSV: {str(e)}'))
            logger.error(f'CSV import error: {e}', exc_info=True)

