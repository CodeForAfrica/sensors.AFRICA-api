from django.core.management import BaseCommand
from django.core.cache import cache

from django.conf import settings

from django.db.models import Max

from sensorsafrica.api.models import Node, SensorLocation, LastActiveNodes
from feinstaub.sensors.models import SensorData


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        for data in (
            SensorData.objects
                .filter(sensordatavalues__value_type__in=["P1", "P2"])
                .values("sensor__node", "location")
                .order_by("sensor__node__id", "location__id")
                .annotate(timestamp=Max("timestamp"))
        ):
            LastActiveNodes.objects.update_or_create(
                node=Node(pk=data["sensor__node"]),
                location=SensorLocation(pk=data["location"]),
                defaults={"last_data_received_at": data["timestamp"]},
            )
