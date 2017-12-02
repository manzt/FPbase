# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-14 04:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='pmid',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True, verbose_name='PMID'),
        ),
    ]
