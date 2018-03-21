# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0004_relate_newsarticles_sources'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScraperResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('completed_time', models.DateTimeField(auto_now_add=True)),
                ('success', models.BooleanField()),
                ('added_count', models.PositiveSmallIntegerField(default=0)),
                ('error_count', models.PositiveSmallIntegerField(default=0)),
                ('total_count', models.PositiveSmallIntegerField(default=0)),
                ('output', models.TextField(blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='newsscraper',
            name='news_source',
        ),
        migrations.AlterModelOptions(
            name='newssource',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.CharField(default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='newssource',
            name='short_name',
            field=models.CharField(max_length=256, db_index=True),
        ),
        migrations.DeleteModel(
            name='NewsScraper',
        ),
        migrations.AddField(
            model_name='scraperresult',
            name='news_source',
            field=models.ForeignKey(to='newsarticles.NewsSource'),
        ),
    ]
