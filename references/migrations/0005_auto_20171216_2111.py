# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-16 21:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0004_auto_20171216_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='initials',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='author',
            unique_together=set([('family', 'initials')]),
        ),
    ]
