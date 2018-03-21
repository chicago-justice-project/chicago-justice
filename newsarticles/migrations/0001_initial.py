# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feedname', models.CharField(db_index=True, max_length=1, choices=[(b'A', b'ABC Local'), (b'C', b'Beachwood Reporter'), (b'L', b'CBS Local'), (b'D', b'Chicago Defender'), (b'M', b'Chicago Magazine'), (b'J', b'Chicago Journal'), (b'O', b'Chicago Now'), (b'E', b'Chicago Reader'), (b'X', b'Chicago Reporter'), (b'R', b'Crains'), (b'I', b'DNAInfo Chicago'), (b'F', b'Fox Chicago'), (b'B', b'NBC Local'), (b'N', b'Chicago News Cooperative'), (b'S', b'Chicago Sun-Times'), (b'T', b'Chicago Tribune'), (b'Z', b'WBEZ'), (b'G', b'WGN TV'), (b'V', b'Windy City Times'), (b'U', b'WLS AM'), (b'W', b'WTTW'), (b'a', b'Daily Herald'), (b'b', b'Better Government Association')])),
                ('url', models.CharField(unique=True, max_length=1024, db_index=True)),
                ('orig_html', models.TextField()),
                ('title', models.TextField()),
                ('bodytext', models.TextField()),
                ('relevant', models.BooleanField(db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category_name', models.CharField(max_length=256)),
                ('abbreviation', models.CharField(max_length=5)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['abbreviation'],
            },
        ),
        migrations.AddField(
            model_name='article',
            name='categories',
            field=models.ManyToManyField(to='newsarticles.Category'),
        ),
    ]
