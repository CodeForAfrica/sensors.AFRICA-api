from django.core.management import BaseCommand

from django.db import connection
from django.db.models import Max
from django.utils import timezone
from datetime import timedelta
from sensorsafrica.api.models import Node, SensorLocation, LastActiveNodes


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        from feinstaub.sensors.models import SensorData, SensorDataValue

        five_min_ago = timezone.now() - timedelta(minutes=5)

        latest = (
            SensorDataValue.objects
            .filter(value_type__in=('P1', 'P2'))
            .filter(sensordata__timestamp__gte=five_min_ago)
            .values('sensordata__sensor__node__id', 'sensordata__sensor__node__location__id')
            .annotate(last_active_date=Max('sensordata__timestamp'))
        )

        for data in latest:
            LastActiveNodes.objects.update_or_create(
                node=Node(pk=data['sensordata__sensor__node__id']),
                location=SensorLocation(pk=data['sensordata__sensor__node__location__id']),
                defaults={"last_data_received_at": data['last_active_date']},
            )
