# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-06 15:43
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0014_auto_20171205_0258'),
    ]

    operations = [
        migrations.AddField(
            model_name='protein',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
        ),
    ]
