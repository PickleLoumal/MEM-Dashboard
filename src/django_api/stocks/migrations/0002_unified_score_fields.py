from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockscore',
            name='execution_date',
            field=models.DateField(blank=True, help_text='Suggested execution date (typically T+1)', null=True),
        ),
        migrations.AddField(
            model_name='stockscore',
            name='score_components',
            field=models.JSONField(blank=True, default=dict, help_text='Component breakdown with raw/weighted contributions'),
        ),
        migrations.AddField(
            model_name='stockscore',
            name='signal_date',
            field=models.DateField(blank=True, help_text='Signal generation date', null=True),
        ),
        migrations.AddField(
            model_name='stockscore',
            name='stop_loss_price',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Stop-loss trigger price', max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='stockscore',
            name='suggested_position_pct',
            field=models.DecimalField(blank=True, decimal_places=4, help_text='Suggested position percentage (0-1)', max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='stockscore',
            name='take_profit_price',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Take-profit trigger price', max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='stockscore',
            name='total_score',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Unified score (-100 to +100)', max_digits=6),
        ),
    ]
