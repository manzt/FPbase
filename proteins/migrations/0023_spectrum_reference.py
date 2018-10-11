# Generated by Django 2.0.9 on 2018-10-09 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0003_auto_20180804_0203'),
        ('proteins', '0022_osermeasurement'),
    ]

    operations = [
        migrations.AddField(
            model_name='spectrum',
            name='reference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='spectra', to='references.Reference'),
        ),
    ]
