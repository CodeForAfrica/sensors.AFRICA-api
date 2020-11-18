from django.core.management import BaseCommand
from django.db.models import Avg, Count, FloatField, Max, Min, Q
from django.db.models.functions import Cast, TruncHour
from django.utils.text import slugify
from feinstaub.sensors.models import Node, Sensor, SensorDataValue, SensorLocation
from ...api.models import SensorDataStat

from django.core.paginator import Paginator

date = 'sonos'

def map_stat(stat, city):
    return SensorDataStat(
        city_slug=slugify(city),
        timestamp=stat["timestamp"],
        value_type=stat["value_type"],
        location=SensorLocation(pk=stat["sensordata__location"]),
        sensor=Sensor(pk=stat["sensordata__sensor"]),
        node=Node(pk=stat["sensordata__sensor__node"]),
        average=stat["average"],
        minimum=stat["minimum"],
        maximum=stat["maximum"],
        sample_size=stat["sample_size"],
        last_datetime=stat["last_datetime"],
    )


def chunked_iterator(queryset, chunk_size=100):
    paginator = Paginator(queryset, chunk_size)
    for page in range(1, paginator.num_pages + 1):
        yield paginator.page(page).object_list


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

            # last_date_time = (
            #     SensorDataStat.objects.filter(city_slug=slugify(city))
            #     .values_list("last_datetime", flat=True)
            #     .order_by("-last_datetime")[:1]
            # )

            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> STARTING BATCH')

            last_date_time = '2020-11-01 00:00:00'
            end_date_time = '2020-11-17 23:59:59'

            print('start time>>>>>>>>>>>>>>>>>>> ', last_date_time)
            print('end time>>>>>>>>>>>>>>>>>>> ', end_date_time)

            queryset = SensorDataValue.objects.filter(
                    Q(sensordata__location__city__iexact=city),
                    # Get dates greater than last stat calculation
                    Q(created__gt=last_date_time),
                    # TODO: Remove this code after data migration is completed
                    Q(created__lt=end_date_time),
                    # Ignore timestamp values
                    ~Q(value_type="timestamp"),
                    # Match only valid float text
                    Q(value__regex=r"^\-?\d+(\.?\d+)?$"),
                )

            # if last_date_time:
            #     queryset = SensorDataValue.objects.filter(
            #         Q(sensordata__location__city__iexact=city),
            #         # Get dates greater than last stat calculation
            #         Q(created__gt=last_date_time),
            #         # TODO: Remove this code after data migration is completed
            #         Q(created__lt=end_date_time),
            #         # Ignore timestamp values
            #         ~Q(value_type="timestamp"),
            #         # Match only valid float text
            #         Q(value__regex=r"^\-?\d+(\.?\d+)?$"),
            #     )
            # else:
            #     queryset = SensorDataValue.objects.filter(
            #         Q(sensordata__location__city__iexact=city),
            #         # Ignore timestamp values
            #         # TODO: Remove this code after data migration is completed
            #         Q(created__lt=end_date_time),
            #         ~Q(value_type="timestamp"),
            #         # Match only valid float text
            #         Q(value__regex=r"^\-?\d+(\.?\d+)?$"),
            #     )

            for stats in chunked_iterator(
                queryset.annotate(timestamp=TruncHour("created"))
                    .values(
                        "timestamp",
                        "value_type",
                        "sensordata__sensor",
                        "sensordata__location",
                        "sensordata__sensor__node",
                    )
                    .order_by()
                    .annotate(
                        last_datetime=Max("created"),
                        average=Avg(Cast("value", FloatField())),
                        minimum=Min(Cast("value", FloatField())),
                        maximum=Max(Cast("value", FloatField())),
                        sample_size=Count("created", FloatField()),
                    )
                    .filter(
                        ~Q(average=float("NaN")),
                        ~Q(minimum=float("NaN")),
                        ~Q(maximum=float("NaN")),
                    )
                    .order_by("timestamp")):
                print('STATS>>>>>>>>>>>>', stats)
                SensorDataStat.objects.bulk_create(
                    list(map(lambda stat: map_stat(stat, city), stats))
                )
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FINISHING BATCH')
