# Manual migration to skip the problematic unique_together constraint
# This migration handles the remaining constraint issue by using a no-op approach
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csi300', '0005_manual_field_updates'),
    ]

    operations = [
        # Django keeps trying to alter unique_together but the constraint doesn't exist
        # in the way Django expects due to the raw SQL table creation in migration 0002.
        # We'll use a no-op SQL statement to satisfy Django's migration system
        # without actually changing the database structure.
        
        migrations.RunSQL(
            sql="SELECT 1; -- Skip unique_together constraint modification - table structure is already correct",
            reverse_sql="SELECT 1; -- No reverse operation needed",
        ),
    ]
