from django.core.management import BaseCommand
from django.core.cache import cache

from django.conf import settings

from django.db.models import Max

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

        print(settings.STATIC_ROOT + "/partial_nodes_data.json")

        with open(settings.STATIC_ROOT + "/partial_nodes_data.json", "w") as f:
            nodes_data = list(
                SensorData.objects.values(
                    "sensor__node",
                    "location__id",
                    "location__location",
                    "location__city",
                    "location__longitude",
                    "location__latitude",
                )
                .order_by("sensor__node__id", "location__id")
                .annotate(timestamp=Max("timestamp"))
            )

            json.dump(nodes_data, f, cls=Encoder)
