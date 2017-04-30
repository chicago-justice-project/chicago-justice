# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from newsarticles.utils.migration import queryset_iterator

def convert_coding(article, coding_cls):
    if article.relevant != False and article.categories.count() == 0:
        return None

    if hasattr(article, 'usercoding'):
        return None

    coding = coding_cls(article=article, date=article.last_modified,
                        relevant=article.relevant)
    coding.save()
    coding.categories = article.categories.all()
    return coding

def create_initial_usercodings(apps, schema_editor):
    Article = apps.get_model('newsarticles', 'Article')
    UserCoding = apps.get_model('newsarticles', 'UserCoding')

    large_queryset = queryset_iterator(Article.objects, chunksize=500)
    for article in large_queryset:
        coding = convert_coding(article, UserCoding)
        print('Coding for {}: {}'.format(article.url, coding))

def reverse_create_initial(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0006_add_usercoding'),
    ]

    operations = [
        migrations.RunPython(create_initial_usercodings, reverse_create_initial)
    ]
