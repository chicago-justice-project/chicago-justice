# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frequency', models.IntegerField()),
                ('article', models.ForeignKey(to='newsarticles.Article')),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word', models.CharField(unique=True, max_length=255, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='articleword',
            name='word',
            field=models.ForeignKey(to='textanalysis.Word'),
        ),
        migrations.AlterUniqueTogether(
            name='articleword',
            unique_together=set([('word', 'article')]),
        ),
    ]
