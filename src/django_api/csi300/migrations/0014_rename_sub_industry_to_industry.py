from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csi300', '0013_alter_csi300company_im_sector'),
    ]

    operations = [
        migrations.RenameField(
            model_name='csi300company',
            old_name='sub_industry',
            new_name='industry',
        ),
    ]
