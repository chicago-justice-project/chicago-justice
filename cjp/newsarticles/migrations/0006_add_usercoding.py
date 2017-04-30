# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('newsarticles', '0005_add_scraperresult'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCoding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('relevant', models.BooleanField()),
            ],
        ),
        migrations.AlterField(
            model_name='article',
            name='author',
            field=models.CharField(default='', max_length=1024, blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='categories',
            field=models.ManyToManyField(to='newsarticles.Category', blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='feedname',
            field=models.CharField(max_length=1, null=True, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='orig_html',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='relevant',
            field=models.NullBooleanField(db_index=True),
        ),
        migrations.AddField(
            model_name='usercoding',
            name='article',
            field=models.OneToOneField(to='newsarticles.Article'),
        ),
        migrations.AddField(
            model_name='usercoding',
            name='categories',
            field=models.ManyToManyField(to='newsarticles.Category', blank=True),
        ),
        migrations.AddField(
            model_name='usercoding',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='usercoding',
            unique_together=set([('article', 'user')]),
        ),
    ]
