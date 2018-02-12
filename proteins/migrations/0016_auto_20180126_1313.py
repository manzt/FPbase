# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-26 13:13
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0015_auto_20180125_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bleachmeasurement',
            name='in_cell',
            field=models.IntegerField(blank=True, choices=[(-1, 'Unkown'), (0, 'No'), (1, 'Yes')], default=-1, help_text='protein expressed in living cells', verbose_name='In cells?'),
        ),
        migrations.AlterField(
            model_name='bleachmeasurement',
            name='power',
            field=models.FloatField(blank=True, help_text="If not reported, use '-1'", null=True, validators=[django.core.validators.MinValueValidator(-1)], verbose_name='Illumination Power'),
        ),
        migrations.AlterField(
            model_name='bleachmeasurement',
            name='rate',
            field=models.FloatField(help_text='Photobleaching half-life (s)', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3000)], verbose_name='Bleach Rate'),
        ),
        migrations.AlterField(
            model_name='bleachmeasurement',
            name='state',
            field=models.ForeignKey(help_text='The state on which this measurement was made', on_delete=django.db.models.deletion.CASCADE, related_name='bleach_measurements', to='proteins.State', verbose_name='Protein (state)'),
        ),
    ]