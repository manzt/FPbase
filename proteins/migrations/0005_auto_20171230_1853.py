# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-30 18:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0004_auto_20171218_0116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protein',
            name='default_state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parent_protein', to='proteins.State'),
        ),
    ]