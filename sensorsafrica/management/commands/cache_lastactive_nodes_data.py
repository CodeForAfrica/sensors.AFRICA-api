from django.core.management import BaseCommand
from django.core.cache import cache

from django.conf import settings

from django.db.models import Max

from sensorsafrica.api.models import Node, SensorLocation, LastActiveNodes
from feinstaub.sensors.models import SensorData

import json
import datetime
from decimal import Decimal


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.timestamp()
        return super(Encoder, self).default(o)


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        for data in (
            SensorData.objects.values("sensor__node", "location")
            .order_by("sensor__node__id", "location__id")
            .annotate(timestamp=Max("timestamp"))
        ):
            LastActiveNodes.objects.update_or_create(
                node=Node(pk=data["sensor__node"]),
                location=SensorLocation(pk=data["location"]),
                last_data_received_at=data["timestamp"],
            )
