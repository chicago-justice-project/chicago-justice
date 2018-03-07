# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0007_populate_usercodings'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='category',
            name='kind',
            field=models.CharField(default='other', max_length=50, choices=[('crimes', 'Crimes'), ('orgs', 'Justice Agencies / Agencies'), ('policing', 'Policing'), ('other', 'Misc.')]),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['kind', 'abbreviation']},
        ),
        migrations.RenameField(
            model_name='category',
            old_name='category_name',
            new_name='title',
        ),
    ]
