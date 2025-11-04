from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScoreCalculationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calculation_date', models.DateField(help_text='Date of the scoring batch', unique=True)),
                ('start_time', models.DateTimeField(help_text='Start timestamp of the batch')),
                ('end_time', models.DateTimeField(blank=True, help_text='End timestamp of the batch', null=True)),
                ('status', models.CharField(choices=[('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], default='running', help_text='Status of the batch', max_length=20)),
                ('total_stocks', models.PositiveIntegerField(default=0, help_text='Number of stocks processed')),
                ('successful_stocks', models.PositiveIntegerField(default=0, help_text='Number of successful stock updates')),
                ('failed_stocks', models.PositiveIntegerField(default=0, help_text='Number of stocks that failed to process')),
                ('error_message', models.TextField(blank=True, help_text='Error message if the run failed')),
            ],
            options={
                'verbose_name': 'Score Calculation Log',
                'verbose_name_plural': 'Score Calculation Logs',
                'db_table': 'score_calculation_logs',
                'ordering': ('-calculation_date',),
            },
        ),
        migrations.CreateModel(
            name='StockScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calculation_date', models.DateField(help_text='Date of the score calculation')),
                ('ticker', models.CharField(help_text='Stock ticker/symbol', max_length=50)),
                ('company_name', models.CharField(help_text='Company name', max_length=255)),
                ('buy_score', models.PositiveSmallIntegerField(default=0, help_text='Buy signal score (0-100)')),
                ('buy_reasons', models.JSONField(blank=True, default=list, help_text='Triggered buy signal reasons')),
                ('sell_score', models.PositiveSmallIntegerField(default=0, help_text='Sell signal score (0-100)')),
                ('sell_reasons', models.JSONField(blank=True, default=list, help_text='Triggered sell signal reasons')),
                ('last_close', models.DecimalField(blank=True, decimal_places=6, help_text='Previous close price', max_digits=20, null=True)),
                ('last_trading_date', models.DateField(blank=True, help_text='Last trading date in the dataset', null=True)),
                ('cmf_value', models.DecimalField(blank=True, decimal_places=6, help_text='Latest CMF value', max_digits=12, null=True)),
                ('obv_value', models.BigIntegerField(blank=True, help_text='Latest OBV value', null=True)),
                ('ma5', models.DecimalField(blank=True, decimal_places=6, help_text='MA5 value', max_digits=20, null=True)),
                ('ma10', models.DecimalField(blank=True, decimal_places=6, help_text='MA10 value', max_digits=20, null=True)),
                ('recommended_action', models.CharField(blank=True, help_text='Resulting recommended action', max_length=50)),
                ('recommended_action_detail', models.TextField(blank=True, help_text='Detailed recommended action explanation')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Stock Score',
                'verbose_name_plural': 'Stock Scores',
                'db_table': 'stock_scores',
                'ordering': ('-calculation_date', 'ticker'),
                'unique_together': {('calculation_date', 'ticker')},
            },
        ),
    ]
