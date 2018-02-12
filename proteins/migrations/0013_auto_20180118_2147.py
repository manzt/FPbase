# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-18 21:47
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0012_auto_20180118_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protein',
            name='pdb',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=4), blank=True, null=True, size=None, verbose_name='Protein DataBank ID'),
        ),
        migrations.AlterField(
            model_name='protein',
            name='uniprot',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True, validators=[django.core.validators.RegexValidator('[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}', 'Not a valid UniProt Accession')], verbose_name='UniProtKB Accession'),
        ),
    ]