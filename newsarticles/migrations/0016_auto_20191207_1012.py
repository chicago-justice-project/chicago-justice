# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-12-07 10:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0015_auto_20190917_2109'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainedSentiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('api_response', models.TextField()),
                ('police_entity_number', models.IntegerField(blank=True, null=True)),
                ('police_entity_words', models.TextField(blank=True)),
                ('sentiment', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='trainedcoding',
            name='bin',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='trainedsentiment',
            name='coding',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsarticles.TrainedCoding'),
        ),
    ]
