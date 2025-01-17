# Generated by Django 2.1.2 on 2018-12-05 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0036_lineage_root_node'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protein',
            name='cofactor',
            field=models.CharField(blank=True, choices=[('bv', 'Biliverdin'), ('fl', 'Flavin'), ('pcb', 'Phycocyanobilin')], help_text='Required for fluorescence', max_length=2),
        ),
    ]
