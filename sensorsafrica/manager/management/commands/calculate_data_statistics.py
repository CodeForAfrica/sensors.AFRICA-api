import math

from django.core.management import BaseCommand
from django.db.models import Avg, F, FloatField, Max, Min, Q
from django.db.models.functions import Cast
from django.utils.text import slugify
from feinstaub.sensors.models import Node, Sensor, SensorDataValue, SensorLocation
from sensorsafrica.data.models import SensorDataStat


def map_stat(stat, city):
    return SensorDataStat(
        city_slug=slugify(city),
        date=stat["date"],
        value_type=stat["value_type"],
        location=SensorLocation(pk=stat["sensordata__location"]),
        sensor=Sensor(pk=stat["sensordata__sensor"]),
        latitude=stat["sensordata__location__latitude"],
        longitude=stat["sensordata__location__longitude"],
        node=Node(pk=stat["sensordata__sensor__node"]),
        average=stat["average"],
        minimum=stat["minimum"],
        maximum=stat["maximum"],
    )


class Command(BaseCommand):
    help = "Calculate and store data statistics"

    def handle(self, *args, **options):

        cities = list(
            set(
                SensorLocation.objects.all()
                .values_list("city", flat=True)
                .order_by("city")
            )
        )

        for city in cities:
            if not city:
                continue

            last_date = (
                SensorDataStat.objects.filter(city_slug=slugify(city))
                .values_list("date", flat=True)
                .order_by("-date")[:1]
            )

            if last_date:
                queryset = SensorDataValue.objects.filter(
                    Q(sensordata__location__city__iexact=city),
                    # Get dates greater than last stat calculation
                    Q(created__date__gt=last_date),
                    # Ignore timestamp values
                    ~Q(value_type="timestamp"),
                    # Match only valid float text
                    Q(value__regex=r"^\-?\d+(\.?\d+)?$"),
                )
            else:
                queryset = SensorDataValue.objects.filter(
                    Q(sensordata__location__city__iexact=city),
                    # Ignore timestamp values
                    ~Q(value_type="timestamp"),
                    # Match only valid float text
                    Q(value__regex=r"^\-?\d+(\.?\d+)?$"),
                )

            stats = list(
                queryset.datetimes("created", "day")
                .values(
                    "datetimefield",
                    "value_type",
                    "sensordata__sensor",
                    "sensordata__location",
                    "sensordata__location__latitude",
                    "sensordata__location__longitude",
                    "sensordata__sensor__node",
                )
                .order_by()
                .annotate(
                    date=F("datetimefield"),
                    average=Avg(Cast("value", FloatField())),
                    minimum=Min(Cast("value", FloatField())),
                    maximum=Max(Cast("value", FloatField())),
                )
                .order_by("-date")
            )

            if len(stats):
                stats = list(
                    filter(
                        lambda stat: math.isfinite(stat["average"])
                        and math.isfinite(stat["maximum"])
                        and math.isfinite(stat["minimum"]),
                        stats,
                    )
                )
                SensorDataStat.objects.bulk_create(
                    list(map(lambda stat: map_stat(stat, city), stats))
                )
