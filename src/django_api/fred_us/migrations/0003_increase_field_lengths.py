# Generated manually to fix field length limitations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fred_us', '0002_add_indicator_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fredusseriesinfo',
            name='frequency',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='fredusseriesinfo',
            name='seasonal_adjustment',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]




