# Generated by Django 2.0.9 on 2018-10-11 17:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0024_auto_20181011_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='bleachmeasurement',
            name='bandcenter',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Band center of excitation light filter', null=True, validators=[django.core.validators.MinValueValidator(200), django.core.validators.MaxValueValidator(1600)], verbose_name='Band Center (nm)'),
        ),
        migrations.AddField(
            model_name='bleachmeasurement',
            name='bandwidth',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Bandwidth of excitation light filter', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)], verbose_name='Bandwidth (nm)'),
        ),
    ]
