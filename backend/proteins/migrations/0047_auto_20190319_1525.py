# Generated by Django 2.1.7 on 2019-03-19 15:25

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('proteins', '0046_auto_20190121_1341'),
    ]

    operations = [
        migrations.CreateModel(
            name='OcFluorEff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('object_id', models.PositiveIntegerField()),
                ('fluor_name', models.CharField(blank=True, max_length=100)),
                ('ex_eff', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='Excitation Efficiency')),
                ('ex_eff_broad', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='Excitation Efficiency (Broadband)')),
                ('em_eff', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='Emission Efficiency')),
                ('brightness', models.FloatField(blank=True, null=True)),
                ('content_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'proteins'), ('model', 'state')), models.Q(('app_label', 'proteins'), ('model', 'dye')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('oc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proteins.OpticalConfig')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='ocfluoreff',
            unique_together={('oc', 'content_type', 'object_id')},
        ),
    ]
