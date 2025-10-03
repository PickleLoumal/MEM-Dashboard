"""
Django management command to update market cap data for CSI300 companies
from JSON export file.

Usage:
    python manage.py update_market_cap --json-file /path/to/csi300_companies.json
"""

import json
import os
import boto3
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from csi300.models import CSI300Company


class Command(BaseCommand):
    help = 'Update market cap data for CSI300 companies from JSON export file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            help='Path to JSON file containing market cap data'
        )
        parser.add_argument(
            '--s3-bucket',
            type=str,
            default='mem-dashboard-data',
            help='S3 bucket name for JSON file'
        )
        parser.add_argument(
            '--s3-key',
            type=str,
            default='csi300_companies.json',
            help='S3 key for JSON file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        json_data = self.load_json_data(options)
        
        if not json_data:
            raise CommandError("No data loaded from JSON file")
        
        self.update_market_cap_data(json_data, options['dry_run'])

    def load_json_data(self, options):
        """Load JSON data from file or S3"""
        json_file = options.get('json_file')
        
        if json_file and os.path.exists(json_file):
            # Load from local file
            self.stdout.write(f"Loading data from local file: {json_file}")
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Load from S3
            return self.load_from_s3(options['s3_bucket'], options['s3_key'])

    def load_from_s3(self, bucket, key):
        """Load JSON data from S3"""
        try:
            self.stdout.write(f"Loading data from S3: s3://{bucket}/{key}")
            s3_client = boto3.client('s3')
            
            response = s3_client.get_object(Bucket=bucket, Key=key)
            data = response['Body'].read().decode('utf-8')
            return json.loads(data)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to load from S3: {e}")
            )
            return None

    def safe_decimal(self, value):
        """Safely convert value to Decimal"""
        if value is None or value == '':
            return None
        
        try:
            # Handle string values
            if isinstance(value, str):
                # Remove any non-numeric characters except decimal point and minus
                cleaned_value = ''.join(c for c in value if c.isdigit() or c in '.-')
                if not cleaned_value or cleaned_value in ['.', '-', '.-']:
                    return None
                return Decimal(cleaned_value)
            
            # Handle numeric values
            return Decimal(str(value))
            
        except (InvalidOperation, ValueError):
            return None

    def update_market_cap_data(self, json_data, dry_run=False):
        """Update market cap data for all companies"""
        total_companies = len(json_data)
        updated_count = 0
        error_count = 0
        
        self.stdout.write(f"\n{'DRY RUN: ' if dry_run else ''}Processing {total_companies} companies...")
        
        with transaction.atomic():
            for item in json_data:
                if item.get('model') != 'csi300.csi300company':
                    continue
                
                try:
                    fields = item.get('fields', {})
                    ticker = fields.get('ticker')
                    
                    if not ticker:
                        self.stdout.write(
                            self.style.WARNING(f"Skipping item without ticker: {item.get('pk')}")
                        )
                        continue
                    
                    # Get market cap values
                    market_cap_local = self.safe_decimal(fields.get('market_cap_local'))
                    market_cap_usd = self.safe_decimal(fields.get('market_cap_usd'))
                    
                    if market_cap_local is None and market_cap_usd is None:
                        self.stdout.write(
                            self.style.WARNING(f"No valid market cap data for {ticker}")
                        )
                        continue
                    
                    # Find company in database
                    try:
                        company = CSI300Company.objects.get(ticker=ticker)
                        
                        # Check if update is needed
                        needs_update = False
                        old_local = company.market_cap_local
                        old_usd = company.market_cap_usd
                        
                        if market_cap_local is not None and old_local != market_cap_local:
                            needs_update = True
                        if market_cap_usd is not None and old_usd != market_cap_usd:
                            needs_update = True
                        
                        if needs_update:
                            if not dry_run:
                                # Update the company
                                if market_cap_local is not None:
                                    company.market_cap_local = market_cap_local
                                if market_cap_usd is not None:
                                    company.market_cap_usd = market_cap_usd
                                company.save()
                            
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"{'[DRY RUN] ' if dry_run else ''}Updated {ticker} ({company.name}):\n"
                                    f"  Local: {old_local} → {market_cap_local}\n"
                                    f"  USD: {old_usd} → {market_cap_usd}"
                                )
                            )
                        
                    except CSI300Company.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f"Company not found in database: {ticker}")
                        )
                        error_count += 1
                        continue
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing {ticker}: {e}")
                    )
                    error_count += 1
                    continue
            
            if dry_run:
                # Rollback transaction for dry run
                transaction.set_rollback(True)
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'DRY RUN ' if dry_run else ''}SUMMARY:\n"
                f"Total companies processed: {total_companies}\n"
                f"Companies updated: {updated_count}\n"
                f"Errors: {error_count}"
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nThis was a dry run. No changes were made to the database.\n"
                    "Remove --dry-run to apply the changes."
                )
            )