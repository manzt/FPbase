# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-03 15:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0010_auto_20171203_1527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='state',
            name='bleach_conf',
        ),
        migrations.RemoveField(
            model_name='state',
            name='bleach_wide',
        ),
    ]
