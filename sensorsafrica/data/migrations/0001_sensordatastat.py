# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-08 04:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sensors', '0019_auto_20190125_0521'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensorDataStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('city_slug', models.CharField(db_index=True, max_length=255)),
                ('value_type', models.CharField(db_index=True, max_length=255)),
                ('average', models.FloatField()),
                ('maximum', models.FloatField()),
                ('minimum', models.FloatField()),
                ('sample_size', models.IntegerField()),
                ('last_datetime', models.DateTimeField()),
                ('datehour', models.DateTimeField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensors.SensorLocation')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensors.Node')),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensors.Sensor')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]