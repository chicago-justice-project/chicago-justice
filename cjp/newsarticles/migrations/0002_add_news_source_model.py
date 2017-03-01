# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsScraper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(max_length=256)),
                ('enabled', models.BooleanField(default=True)),
                ('scraper_type', models.PositiveSmallIntegerField(choices=[(0, b'BaseScraper')])),
                ('config', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='NewsSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('short_name', models.CharField(max_length=256)),
                ('legacy_feed_id', models.CharField(max_length=8, blank=True, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='newsscraper',
            name='news_source',
            field=models.ForeignKey(to='newsarticles.NewsSource'),
        ),
        migrations.AddField(
            model_name='article',
            name='news_source',
            field=models.ForeignKey(to='newsarticles.NewsSource', null=True),
        ),
    ]
