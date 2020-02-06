# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-12-10 20:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0016_auto_20191207_1012'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainedSentimentEntities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(blank=True, null=True)),
                ('entity', models.TextField(blank=True)),
                ('sentiment', models.FloatField(blank=True, null=True)),
                ('coding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsarticles.TrainedCoding')),
            ],
        ),
        migrations.RemoveField(
            model_name='trainedsentiment',
            name='police_entity_number',
        ),
        migrations.RemoveField(
            model_name='trainedsentiment',
            name='police_entity_words',
        ),
        migrations.RemoveField(
            model_name='trainedsentiment',
            name='sentiment',
        ),
        migrations.AddField(
            model_name='trainedsentimententities',
            name='response',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsarticles.TrainedSentiment'),
        ),
    ]
