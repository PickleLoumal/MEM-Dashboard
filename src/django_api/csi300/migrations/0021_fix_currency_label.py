from django.db import migrations


def fix_currency_label(apps, schema_editor):
    company_model = apps.get_model('csi300', 'CSI300Company')
    company_model.objects.filter(currency='Chinese Re').update(currency='Chinese Renminbi')


class Migration(migrations.Migration):

    dependencies = [
        ('csi300', '0020_csi300company_region'),
    ]

    operations = [
        migrations.RunPython(fix_currency_label, migrations.RunPython.noop),
    ]
