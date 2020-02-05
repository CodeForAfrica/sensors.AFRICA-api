from django.core.management import BaseCommand

from django.db import connection
from sensorsafrica.api.models import Node, SensorLocation, LastActiveNodes


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT
                        sn.id,
                        sn.location_id,
                        MAX("timestamp") AS last_active_date
                    FROM
                        sensors_sensordata sd
                        INNER JOIN sensors_sensor s ON s.id = sd.sensor_id
                            INNER JOIN sensors_node sn ON sn.id = s.node_id
                            INNER JOIN sensors_sensordatavalue sv ON sv.sensordata_id = sd.id
                            AND sv.value_type in ('P1', 'P2')
                        WHERE
                            "timestamp" >= now() - INTERVAL '5 min'
                        GROUP BY
                            sn.id
                """)
            latest = cursor.fetchall()
            for data in latest:
                LastActiveNodes.objects.update_or_create(
                    node=Node(pk=data[0]),
                    location=SensorLocation(pk=data[1]),
                    defaults={"last_data_received_at": data[2]},
                )
