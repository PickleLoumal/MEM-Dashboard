# Manual migration to fix constraint issues
# This migration manually handles the field updates without touching unique_together constraints
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('csi300', '0004_auto_20250926_0330'),
    ]

    operations = [
        # Update all fields to match the current model definition
        # But skip the problematic unique_together constraint modification
        
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='big_trends_events',
            field=models.TextField(default='', help_text='Big trends and events'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='business_overview',
            field=models.TextField(default='', help_text='Business overview'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='business_performance',
            field=models.TextField(default='', help_text='Business performance analysis'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='company',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='investment_summary', to='csi300.csi300company'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='competitive_landscape',
            field=models.TextField(default='', help_text='Competitive landscape'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='customer_segments',
            field=models.TextField(default='', help_text='Customer segments analysis'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='financial_stability',
            field=models.TextField(default='', help_text='Financial stability analysis'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='forecast_outlook',
            field=models.TextField(default='', help_text='Forecast and outlook'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='industry_context',
            field=models.TextField(default='', help_text='Industry context'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='industry_ratio_analysis',
            field=models.TextField(default='', help_text='Industry ratio analysis'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='investment_firms_views',
            field=models.TextField(default='', help_text='Investment firms views'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='key_financials_valuation',
            field=models.TextField(default='', help_text='Key financials and valuation'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='key_takeaways',
            field=models.TextField(default='', help_text='Key takeaways'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='market_cap_display',
            field=models.CharField(default='', help_text='Market cap display format', max_length=100),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='recommended_action',
            field=models.CharField(default='', help_text='Investment recommendation', max_length=50),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='recommended_action_detail',
            field=models.TextField(default='', help_text='Detailed recommendation'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='risks_anomalies',
            field=models.TextField(default='', help_text='Risks and anomalies'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='sources',
            field=models.TextField(default='', help_text='Data sources'),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='stock_price_previous_close',
            field=models.DecimalField(decimal_places=6, default=0, help_text='Previous close price', max_digits=10),
        ),
        migrations.AlterField(
            model_name='csi300investmentsummary',
            name='tariffs_supply_chain_risks',
            field=models.TextField(default='', help_text='Tariffs and supply chain risks'),
        ),
        
        # Note: We intentionally skip the unique_together constraint modification
        # because the table structure created by 0002_fix_investment_summary_structure.py
        # uses a different constraint approach (OneToOneField instead of unique_together)
    ]
