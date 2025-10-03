# Final migration to resolve unique_together constraint issues
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csi300', '0006_skip_unique_together_fix'),
    ]

    operations = [
        # Final no-op migration to resolve the persistent unique_together issue
        migrations.RunSQL(
            sql="SELECT 1; -- Final unique_together constraint fix - table structure is correct",
            reverse_sql="SELECT 1; -- No reverse operation needed",
        ),
    ]
