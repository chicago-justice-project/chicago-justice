# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0008_category_kinds'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercoding',
            name='locations',
            field=models.TextField(default='[]', blank=True),
        ),
    ]
