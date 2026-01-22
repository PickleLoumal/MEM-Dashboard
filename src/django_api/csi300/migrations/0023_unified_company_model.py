"""
Unified Company Model Migration

This migration:
1. Creates a new unified 'company' table with exchange field
2. Creates new 'investment_summary' table
3. Creates new 'generation_task' table
4. Migrates data from old tables (csi300_company, csi300_hshares_company)
5. Preserves old tables as backup (to be deleted in future migration)
"""

import django.db.models.deletion
from django.db import migrations, models


def infer_exchange_from_ticker(ticker, region):
    """Infer exchange code from ticker suffix or region."""
    if ticker:
        ticker_upper = ticker.upper()
        if ticker_upper.endswith(".SH"):
            return "SSE"
        if ticker_upper.endswith(".SZ"):
            return "SZSE"
        if ticker_upper.endswith(".HK"):
            return "HKEX"

    if region:
        region_lower = region.lower()
        if "hong kong" in region_lower:
            return "HKEX"

    return "SSE"  # Default


def migrate_data_forward(apps, schema_editor):
    """Migrate data from old tables to new unified table."""
    # Get models at migration state
    Company = apps.get_model("csi300", "Company")
    InvestmentSummary = apps.get_model("csi300", "InvestmentSummary")
    GenerationTask = apps.get_model("csi300", "GenerationTask")

    # Use raw SQL to check if old tables exist and have data
    from django.db import connection

    cursor = connection.cursor()

    # Track ID mapping for foreign key updates
    old_to_new_company_id = {}

    # Migrate from csi300_company (A-shares)
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'csi300_company'"
    )
    if cursor.fetchone()[0] > 0:
        cursor.execute("SELECT * FROM csi300_company")
        columns = [col[0] for col in cursor.description]

        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            old_id = row_dict.pop("id")
            created_at = row_dict.pop("created_at", None)
            updated_at = row_dict.pop("updated_at", None)

            # Infer exchange
            exchange = infer_exchange_from_ticker(
                row_dict.get("ticker"), row_dict.get("region")
            )

            # Create new company
            new_company = Company(
                exchange=exchange,
                **{k: v for k, v in row_dict.items() if k not in ["id"]},
            )
            new_company.save()

            # Store ID mapping
            old_to_new_company_id[("csi300_company", old_id)] = new_company.id

    # Migrate from csi300_hshares_company (H-shares)
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'csi300_hshares_company'"
    )
    if cursor.fetchone()[0] > 0:
        cursor.execute("SELECT * FROM csi300_hshares_company")
        columns = [col[0] for col in cursor.description]

        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            old_id = row_dict.pop("id")
            row_dict.pop("created_at", None)
            row_dict.pop("updated_at", None)

            # All H-shares are HKEX
            new_company = Company(
                exchange="HKEX",
                **{k: v for k, v in row_dict.items() if k not in ["id"]},
            )
            new_company.save()

            old_to_new_company_id[("csi300_hshares_company", old_id)] = new_company.id

    # Migrate investment summaries
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'csi300_investment_summary'"
    )
    if cursor.fetchone()[0] > 0:
        cursor.execute("SELECT * FROM csi300_investment_summary")
        columns = [col[0] for col in cursor.description]

        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            row_dict.pop("id")
            old_company_id = row_dict.pop("company_id")
            row_dict.pop("created_at", None)
            row_dict.pop("updated_at", None)

            # Get new company ID
            new_company_id = old_to_new_company_id.get(("csi300_company", old_company_id))
            if new_company_id:
                InvestmentSummary.objects.create(
                    company_id=new_company_id,
                    **{k: v for k, v in row_dict.items()},
                )

    # Migrate generation tasks
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'csi300_generation_task'"
    )
    if cursor.fetchone()[0] > 0:
        cursor.execute("SELECT * FROM csi300_generation_task")
        columns = [col[0] for col in cursor.description]

        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            row_dict.pop("id")
            old_company_id = row_dict.pop("company_id")
            row_dict.pop("created_at", None)
            row_dict.pop("updated_at", None)

            # Get new company ID
            new_company_id = old_to_new_company_id.get(("csi300_company", old_company_id))
            if new_company_id:
                GenerationTask.objects.create(
                    company_id=new_company_id,
                    **{k: v for k, v in row_dict.items()},
                )


def migrate_data_backward(apps, schema_editor):
    """Reverse migration - clear new tables (old tables preserved)."""
    Company = apps.get_model("csi300", "Company")
    InvestmentSummary = apps.get_model("csi300", "InvestmentSummary")
    GenerationTask = apps.get_model("csi300", "GenerationTask")

    GenerationTask.objects.all().delete()
    InvestmentSummary.objects.all().delete()
    Company.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("csi300", "0022_add_generation_task_model"),
    ]

    operations = [
        # Create new Company table
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "exchange",
                    models.CharField(
                        choices=[
                            ("SSE", "上海证券交易所"),
                            ("SZSE", "深圳证券交易所"),
                            ("HKEX", "香港交易所"),
                        ],
                        db_index=True,
                        default="SSE",
                        help_text="Stock exchange code (SSE, SZSE, HKEX)",
                        max_length=10,
                    ),
                ),
                ("name", models.CharField(help_text="Company name", max_length=200)),
                (
                    "ticker",
                    models.CharField(
                        blank=True, help_text="Stock ticker", max_length=20, null=True
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        blank=True,
                        help_text="Region (e.g., Mainland China, Hong Kong)",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "im_sector",
                    models.CharField(
                        blank=True,
                        help_text="IM Sector (combined from im_code and industry)",
                        max_length=150,
                        null=True,
                    ),
                ),
                (
                    "industry",
                    models.CharField(
                        blank=True, help_text="Industry", max_length=500, null=True
                    ),
                ),
                (
                    "gics_industry",
                    models.CharField(
                        blank=True, help_text="GICS Industry", max_length=100, null=True
                    ),
                ),
                (
                    "gics_sub_industry",
                    models.CharField(
                        blank=True, help_text="GICS Sub-industry", max_length=100, null=True
                    ),
                ),
                (
                    "naming",
                    models.CharField(
                        blank=True, help_text="Company naming", max_length=200, null=True
                    ),
                ),
                (
                    "business_description",
                    models.TextField(blank=True, help_text="Business description", null=True),
                ),
                (
                    "company_info",
                    models.TextField(blank=True, help_text="Company info", null=True),
                ),
                (
                    "directors",
                    models.CharField(
                        blank=True, help_text="Directors", max_length=500, null=True
                    ),
                ),
                (
                    "price_local_currency",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Price in local currency (Open)",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "previous_close",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Previous close price",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        blank=True, help_text="Currency", max_length=20, null=True
                    ),
                ),
                (
                    "total_return_2018_to_2025",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Total return 2018-2025",
                        max_digits=15,
                        null=True,
                    ),
                ),
                (
                    "last_trade_date",
                    models.DateField(blank=True, help_text="Last trade date", null=True),
                ),
                (
                    "price_52w_high",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="52-week high",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "price_52w_low",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="52-week low",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "market_cap_local",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Market cap (local)",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "market_cap_usd",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Market cap (USD)",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "total_revenue_local",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total revenue (local)",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "ltm_revenue_local",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="LTM revenue (local)",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "ntm_revenue_local",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="NTM revenue (local)",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "total_assets_local",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total assets (local)",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "net_assets_local",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Net assets (local)",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "total_debt_local",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total debt (local)",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "net_profits_fy0",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Net profits FY0",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "operating_margin_trailing",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Operating margin (trailing)",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "operating_profits_per_share",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Operating profits per share",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "eps_trailing",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="EPS trailing",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "eps_actual_fy0",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="EPS actual FY0",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "eps_forecast_fy1",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="EPS forecast FY1",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "eps_growth_percent",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="EPS growth %",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "asset_turnover_ltm",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Asset turnover LTM",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "roa_trailing",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="ROA trailing",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "roe_trailing",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="ROE trailing",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "operating_leverage",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Operating leverage",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "altman_z_score_manufacturing",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Altman Z-score (manufacturing)",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "altman_z_score_non_manufacturing",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Altman Z-score (non-manufacturing)",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "ebitda_fy0",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="EBITDA FY0",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "ebitda_fy_minus_1",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="EBITDA FY-1",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "cash_flow_operations_fy0",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Cash flow operations FY0",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "cash_flow_operations_fy_minus_1",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Cash flow operations FY-1",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "interest_expense_fy0",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Interest expense FY0",
                        max_digits=20,
                        null=True,
                    ),
                ),
                (
                    "effective_interest_rate",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Effective interest rate",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "interest_coverage_ratio",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Interest coverage ratio",
                        max_digits=15,
                        null=True,
                    ),
                ),
                (
                    "debt_to_total_assets",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Debt to total assets",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "debt_to_equity",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Debt to equity",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "current_ratio",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Current ratio",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "quick_ratio",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Quick ratio",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "pe_ratio_trailing",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="P/E ratio trailing",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "pe_ratio_consensus",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="P/E ratio consensus",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "peg_ratio",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="PEG ratio",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "dividend_yield_fy0",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Dividend yield FY0",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "dividend_payout_ratio",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Dividend payout ratio",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "dividend_local_currency",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Dividend (local currency)",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "dividend_3yr_cagr",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Dividend 3yr CAGR",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "dividend_5yr_cagr",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Dividend 5yr CAGR",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "dividend_10yr_cagr",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Dividend 10yr CAGR",
                        max_digits=10,
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Company",
                "verbose_name_plural": "Companies",
                "db_table": "company",
                "ordering": ["exchange", "ticker"],
            },
        ),
        # Add indexes and constraints for Company
        migrations.AddIndex(
            model_name="company",
            index=models.Index(fields=["exchange"], name="company_exchange_idx"),
        ),
        migrations.AddIndex(
            model_name="company",
            index=models.Index(fields=["ticker"], name="company_ticker_idx"),
        ),
        migrations.AddIndex(
            model_name="company",
            index=models.Index(fields=["im_sector"], name="company_im_sector_idx"),
        ),
        migrations.AddConstraint(
            model_name="company",
            constraint=models.UniqueConstraint(
                fields=("exchange", "ticker"), name="unique_exchange_ticker"
            ),
        ),
        # Create new InvestmentSummary table
        migrations.CreateModel(
            name="InvestmentSummary",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("report_date", models.DateField(help_text="Report date")),
                (
                    "stock_price_previous_close",
                    models.DecimalField(
                        decimal_places=6,
                        default=0,
                        help_text="Previous close price",
                        max_digits=10,
                    ),
                ),
                (
                    "market_cap_display",
                    models.CharField(
                        default="", help_text="Market cap display format", max_length=200
                    ),
                ),
                (
                    "recommended_action",
                    models.CharField(
                        default="", help_text="Investment recommendation", max_length=50
                    ),
                ),
                (
                    "recommended_action_detail",
                    models.TextField(default="", help_text="Detailed recommendation"),
                ),
                (
                    "business_overview",
                    models.TextField(default="", help_text="Business overview"),
                ),
                (
                    "business_performance",
                    models.TextField(default="", help_text="Business performance analysis"),
                ),
                (
                    "industry_context",
                    models.TextField(default="", help_text="Industry context"),
                ),
                (
                    "financial_stability",
                    models.TextField(default="", help_text="Financial stability analysis"),
                ),
                (
                    "key_financials_valuation",
                    models.TextField(default="", help_text="Key financials and valuation"),
                ),
                (
                    "big_trends_events",
                    models.TextField(default="", help_text="Big trends and events"),
                ),
                (
                    "customer_segments",
                    models.TextField(default="", help_text="Customer segments analysis"),
                ),
                (
                    "competitive_landscape",
                    models.TextField(default="", help_text="Competitive landscape"),
                ),
                (
                    "risks_anomalies",
                    models.TextField(default="", help_text="Risks and anomalies"),
                ),
                (
                    "forecast_outlook",
                    models.TextField(default="", help_text="Forecast and outlook"),
                ),
                (
                    "investment_firms_views",
                    models.TextField(default="", help_text="Investment firms views"),
                ),
                (
                    "industry_ratio_analysis",
                    models.TextField(default="", help_text="Industry ratio analysis"),
                ),
                (
                    "tariffs_supply_chain_risks",
                    models.TextField(default="", help_text="Tariffs and supply chain risks"),
                ),
                (
                    "key_takeaways",
                    models.TextField(default="", help_text="Key takeaways"),
                ),
                ("sources", models.TextField(default="", help_text="Data sources")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="investment_summary",
                        to="csi300.company",
                    ),
                ),
            ],
            options={
                "verbose_name": "Investment Summary",
                "verbose_name_plural": "Investment Summaries",
                "db_table": "investment_summary",
                "ordering": ["-report_date"],
            },
        ),
        # Create new GenerationTask table (referencing new Company)
        migrations.CreateModel(
            name="GenerationTask",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "task_id",
                    models.CharField(
                        db_index=True,
                        help_text="UUID task identifier",
                        max_length=36,
                        unique=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        db_index=True,
                        default="pending",
                        help_text="Current task status",
                        max_length=20,
                    ),
                ),
                (
                    "progress_message",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Current progress message",
                        max_length=500,
                    ),
                ),
                (
                    "progress_percent",
                    models.IntegerField(default=0, help_text="Progress percentage (0-100)"),
                ),
                (
                    "result_data",
                    models.JSONField(
                        blank=True, help_text="Task result data (on success)", null=True
                    ),
                ),
                (
                    "error_message",
                    models.TextField(
                        blank=True, default="", help_text="Error message (on failure)"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "completed_at",
                    models.DateTimeField(
                        blank=True, help_text="Task completion time", null=True
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        help_text="Company being processed",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="generation_tasks",
                        to="csi300.company",
                    ),
                ),
            ],
            options={
                "verbose_name": "Generation Task",
                "verbose_name_plural": "Generation Tasks",
                "db_table": "generation_task",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="generationtask",
            index=models.Index(
                fields=["status", "created_at"], name="generation__status_idx"
            ),
        ),
        # Migrate data from old tables to new tables
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
        # Remove old models from Django state (tables preserved as backup)
        # Note: We don't delete old tables - they serve as backup
        # Old tables: csi300_company, csi300_hshares_company, csi300_investment_summary, csi300_generation_task
    ]
