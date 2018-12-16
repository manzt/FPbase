# Generated by Django 2.1.2 on 2018-12-16 17:44

from django.db import migrations


def make_many_exerpts(apps, schema_editor):
    """
        Adds the Author object in Book.author to the
        many-to-many relationship in Book.authors
    """
    Excerpt = apps.get_model('proteins', 'Excerpt')

    for excerpt in Excerpt.objects.all():
        excerpt.proteins.add(excerpt.protein)


class Migration(migrations.Migration):

    dependencies = [
        ('proteins', '0041_auto_20181216_1743'),
    ]

    operations = [
        migrations.RunPython(make_many_exerpts),
    ]
