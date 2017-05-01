# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textanalysis', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='articleword',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='articleword',
            name='article',
        ),
        migrations.RemoveField(
            model_name='articleword',
            name='word',
        ),
        migrations.DeleteModel(
            name='ArticleWord',
        ),
        migrations.DeleteModel(
            name='Word',
        ),
    ]
