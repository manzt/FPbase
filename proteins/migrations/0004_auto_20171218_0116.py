# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-18 01:16
from __future__ import unicode_literals

from django.db import migrations, models
import proteins.models


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0003_auto_20171217_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='brightness',
            field=models.FloatField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='protein',
            name='seq',
            field=models.CharField(blank=True, help_text='Amino acid sequence (IPG ID is preferred)', max_length=512, null=True, unique=True, validators=[proteins.models.protein_sequence_validator]),
        ),
    ]