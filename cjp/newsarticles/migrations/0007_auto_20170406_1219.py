# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0006_auto_20170405_1636'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usercoding',
            options={'permissions': (('can_code_article', 'Can code news articles'),)},
        ),
        migrations.AlterField(
            model_name='article',
            name='relevant',
            field=models.NullBooleanField(db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='usercoding',
            unique_together=set([('article', 'user')]),
        ),
    ]
