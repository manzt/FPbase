# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-03 15:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0004_auto_20171114_0427'),
        ('proteins', '0008_protein_ipg_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='BleachMeasurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.DecimalField(decimal_places=1, help_text='Photobleaching rate', max_digits=6, verbose_name='Bleach Rate')),
                ('modality', models.CharField(blank=True, help_text='Type of microscopy/illumination used for measurement', max_length=100, null=True, verbose_name='Illumination Modality')),
                ('reference', models.ForeignKey(blank=True, help_text='Reference where the measurement was made', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bleach_measurement', to='references.Reference', verbose_name='Measurement Reference')),
                ('state', models.ForeignKey(help_text='The protein (state) for which this measurement was observed', on_delete=django.db.models.deletion.CASCADE, related_name='bleach_measurement', to='proteins.State', verbose_name='Protein (state)')),
            ],
        ),
    ]