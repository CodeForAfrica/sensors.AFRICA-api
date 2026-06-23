from django.core.management import BaseCommand
from django.core.cache import cache

from django.conf import settings

from django.forms.models import model_to_dict

from feinstaub.sensors.models import SensorLocation, Sensor, SensorType

import os
import json
import datetime
from django.utils import timezone

from django.db import connection

from rest_framework import serializers


class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = "__all__"


class SensorSerializer(serializers.ModelSerializer):
    sensor_type = SensorTypeSerializer()

    class Meta:
        model = Sensor
        fields = "__all__"


class SensorLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorLocation
        fields = "__all__"


class Command(BaseCommand):
    help = ""

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=str)

    def handle(self, *args, **options):
        intervals = {'5m': '5 minutes', '30m': '30 minutes', '1h': '1 hour', '24h': '24 hours'}
        paths = {
            '5m': [
                '../../../static/v2/data.json',
                '../../../static/v2/data.dust.min.json',
                '../../../static/v2/data.temp.min.json'
            ],
            '30m': [
                '../../../static/v2/data.json',
                '../../../static/v2/data.dust.min.json',
                '../../../static/v2/data.temp.min.json'
            ],
            '1h': ['../../../static/v2/data.1h.json'],
            '24h': ['../../../static/v2/data.24h.json']
        }
        cursor = connection.cursor()
        cursor.execute('''
            SELECT sd.sensor_id, sdv.value_type, AVG(CAST(sdv."value" AS FLOAT)) as "value", COUNT("value"), sd.location_id
                FROM sensors_sensordata sd
                    INNER JOIN sensors_sensordatavalue sdv
                        ON  sdv.sensordata_id = sd.id
                            AND sdv.value_type <> 'timestamp'
                            AND sdv.value ~ '^\\-?\\d+(\\.?\\d+)?$'
                WHERE "timestamp" >= (NOW() - interval %s)
                GROUP BY sd.sensor_id, sdv.value_type, sd.location_id
        ''', [intervals[options['interval']]])

        # Fetch all rows once and build maps to avoid N+1 ORM queries
        rows = cursor.fetchall()
        if not rows:
            return

        sensor_ids = set([r[0] for r in rows])
        location_ids = set([r[4] for r in rows if r[4] is not None])

        sensors_qs = Sensor.objects.filter(pk__in=sensor_ids).select_related('sensor_type')
        sensor_map = {s.pk: SensorSerializer(s).data for s in sensors_qs}

        locations_qs = SensorLocation.objects.filter(pk__in=location_ids)
        location_map = {l.pk: SensorLocationSerializer(l).data for l in locations_qs}

        data = {}
        for row in rows:
            sid = row[0]
            val_type = row[1]
            avg_value = row[2]
            sample_count = row[3]
            loc_id = row[4]

            if sid in data:
                data[sid]['sensordatavalues'].append({
                    'samples': sample_count,
                    'value': avg_value,
                    'value_type': val_type,
                })
            else:
                data[sid] = {
                    'location': location_map.get(loc_id) if loc_id in location_map else None,
                    'sensor': sensor_map.get(sid),
                    'sensordatavalues': [{
                        'samples': sample_count,
                        'value': avg_value,
                        'value_type': val_type,
                    }],
                }

        for path in paths[options['interval']]:
            with open(
                os.path.join(os.path.dirname(
                    os.path.abspath(__file__)), path), 'w'
            ) as f:
                if 'dust' in path:
                    json.dump(list(filter(
                        lambda d: d['sensor']['sensor_type']['uid'] == 'sds011', data.values())), f)
                elif 'temp' in path:
                    json.dump(list(filter(
                        lambda d: d['sensor']['sensor_type']['uid'] == 'dht22', data.values())), f)
                else:
                    json.dump(list(data.values()), f)
