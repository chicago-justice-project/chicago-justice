# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import gc

def queryset_iterator(queryset, chunksize=1000):
    """
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    """
    queryset = queryset.order_by('pk')
    last_item = queryset.last()

    if not last_item:
        return

    pk = 0
    while pk < last_item.pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()

def populate_articles(apps, schema_editor):
    Article = apps.get_model('newsarticles', 'Article')
    NewsSource = apps.get_model('newsarticles', 'NewsSource')

    # Cache sources
    sources = {}
    unknown_source = None

    for ns in NewsSource.objects.all():
        if ns.legacy_feed_id:
            sources[ns.legacy_feed_id] = ns
        else:
            unknown_source = ns

    large_queryset = queryset_iterator(Article.objects, chunksize=500)

    for article in large_queryset:
        article.news_source = sources.get(article.feedname, unknown_source)
        article.save(update_fields=['news_source'])


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0003_populate_original_news_sources'),
    ]

    operations = [
        migrations.RunPython(populate_articles),
    ]
