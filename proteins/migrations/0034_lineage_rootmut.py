# Generated by Django 2.1.2 on 2018-11-07 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0033_auto_20181107_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineage',
            name='rootmut',
            field=models.CharField(blank=True, max_length=400),
        ),
    ]
