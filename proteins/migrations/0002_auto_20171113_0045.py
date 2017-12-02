# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-13 00:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protein',
            name='parent_organism',
            field=models.ForeignKey(blank=True, help_text='Organism from which the protein was engineered', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proteins', to='proteins.Organism', verbose_name='Parental organism'),
        ),
        migrations.AlterField(
            model_name='state',
            name='state_id',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
