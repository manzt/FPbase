# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-15 13:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0008_mutation'),
    ]

    operations = [
        migrations.AddField(
            model_name='protein',
            name='genbank',
            field=models.CharField(blank=True, max_length=12, null=True, unique=True, verbose_name='Genbank Accession'),
        ),
        migrations.AddField(
            model_name='protein',
            name='uniprot',
            field=models.CharField(blank=True, max_length=12, null=True, unique=True, verbose_name='UniProtKB Accession'),
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([('protein', 'ex_max', 'em_max', 'ext_coeff', 'qy')]),
        ),
    ]