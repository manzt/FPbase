# Generated by Django 2.0.5 on 2018-05-15 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0007_auto_20180513_2346'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='dye',
            name='url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='filter',
            name='url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='light',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]
