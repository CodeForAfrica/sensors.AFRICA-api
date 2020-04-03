import datetime
import pytz
import json
from geohash import encode
from random import random

from rest_framework.exceptions import ValidationError

from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum, Avg, Q
from django.db.models.functions import Cast, TruncDate
from rest_framework import mixins, pagination, viewsets

from sensorsafrica.influxclient import client

from rest_framework.response import Response


class PushSensorDataViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    def create(self, request):
        client.write_points([{
            "tags": {
                "node_uid": "0",
                "node_owner": "cfa",
                "sensor_uid": "a",
                "sensor_name": "b",
                "sensor_manufacturer": "c",
                "lat": -6.7924,
                "lng": 39.2083,
                "country": "TZ",
                "city": "dar-es-salaam",
                "geohash": encode(-6.7924, 39.2083)
            },
            "fields": {
                "P2": random() * 50,
                "P1": random() * 50
            },
            "measurement": "pm"
        }])

        return Response({"ok": 1})
