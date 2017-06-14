# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrimeReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orig_ward', models.CharField(max_length=5, db_index=True)),
                ('orig_rd', models.CharField(max_length=20, db_index=True)),
                ('orig_beat_num', models.CharField(max_length=8, db_index=True)),
                ('orig_location_descr', models.CharField(max_length=100, db_index=True)),
                ('orig_fbi_descr', models.CharField(max_length=100, db_index=True)),
                ('orig_domestic_i', models.CharField(max_length=4, db_index=True)),
                ('orig_status', models.CharField(max_length=50, db_index=True)),
                ('orig_street', models.CharField(max_length=100, db_index=True)),
                ('orig_fbi_cd', models.CharField(max_length=10, db_index=True)),
                ('orig_dateocc', models.CharField(max_length=50, db_index=True)),
                ('orig_stnum', models.CharField(max_length=20, db_index=True)),
                ('orig_description', models.CharField(max_length=150, db_index=True)),
                ('orig_stdir', models.CharField(max_length=10, db_index=True)),
                ('orig_curr_iucr', models.CharField(max_length=20, db_index=True)),
                ('web_case_num', models.CharField(max_length=20, db_index=True)),
                ('web_date', models.DateTimeField(db_index=True)),
                ('web_block', models.CharField(max_length=200, db_index=True)),
                ('web_code', models.CharField(max_length=20, db_index=True)),
                ('web_crime_type', models.CharField(max_length=100, db_index=True)),
                ('web_secondary', models.CharField(max_length=150, db_index=True)),
                ('web_arrest', models.CharField(max_length=1, db_index=True)),
                ('web_location', models.CharField(max_length=100, db_index=True)),
                ('web_domestic', models.CharField(max_length=4, db_index=True)),
                ('web_beat', models.CharField(max_length=8, db_index=True)),
                ('web_ward', models.CharField(max_length=5, db_index=True)),
                ('web_nibrs', models.CharField(max_length=11, db_index=True)),
                ('crime_date', models.DateField(db_index=True)),
                ('crime_time', models.TimeField(db_index=True)),
                ('geocode_latitude', models.FloatField(db_index=True)),
                ('geocode_longitude', models.FloatField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='LookupCRBeat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('web_beat', models.CharField(max_length=8, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='LookupCRCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('web_code', models.CharField(max_length=20, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='LookupCRCrimeDateMonth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.SmallIntegerField(db_index=True)),
                ('month', models.SmallIntegerField(db_index=True)),
                ('the_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='LookupCRCrimeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('web_crime_type', models.CharField(max_length=100, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='LookupCRNibrs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('web_nibrs', models.CharField(max_length=11, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='LookupCRSecondary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('web_secondary', models.CharField(max_length=150, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='LookupCRWard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('web_ward', models.CharField(max_length=5, db_index=True)),
            ],
        ),
    ]
