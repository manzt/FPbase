# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-06 21:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import proteins.models


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0018_auto_20171206_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='status',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], default='uncurated', max_length=100, no_check_for_status=True, verbose_name='status'),
        ),
        migrations.AddField(
            model_name='state',
            name='status_changed',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed'),
        ),
        migrations.AlterField(
            model_name='organism',
            name='tax_id',
            field=models.CharField(help_text='NCBI Taxonomy ID (e.g. 6100 for Aequorea victora)', max_length=8, verbose_name='Taxonomy ID'),
        ),
        migrations.AlterField(
            model_name='protein',
            name='gb_prot',
            field=models.CharField(blank=True, help_text='GenBank protein Accession number (e.g. AFR60231)', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='state',
            name='em_spectra',
            field=proteins.models.SpectrumField(blank=True, help_text='Spectrum information as a list of (wavelength, value) pairs, e.g. [(300, 0.5), (301, 0.6),... ]', null=True),
        ),
        migrations.AlterField(
            model_name='state',
            name='ex_spectra',
            field=proteins.models.SpectrumField(blank=True, help_text='Spectrum information as a list of (wavelength, value) pairs, e.g. [(300, 0.5), (301, 0.6),... ]', null=True),
        ),
        migrations.AlterField(
            model_name='state',
            name='name',
            field=models.CharField(default='default', max_length=64),
        ),
    ]
