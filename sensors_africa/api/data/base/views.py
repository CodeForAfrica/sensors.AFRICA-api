import datetime

from django.db.models import Avg, Case, F, FloatField, Max, Min, Q, When
from django.db.models.functions import Cast
from django.utils import timezone
from feinstaub.sensors.models import SensorData, SensorDataValue
from rest_framework import mixins, pagination, viewsets

from .serializers import ReadingsNowSerializer, ReadingsSerializer

value_types = {"air": ["P1", "P2"]}


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class ReadingsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SensorDataValue.objects.none()
    serializer_class = ReadingsSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]
        city = self.request.query_params.get("city")

        sensordata = SensorData.objects.filter(location__city=city)

        now = timezone.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        last = midnight - datetime.timedelta(days=7)

        return (
            SensorDataValue.objects.filter(
                sensordata__in=sensordata,
                value_type__in=value_types[sensor_type],
                created__range=[last, now],
            )
            .extra({"day": "DATE_TRUNC('day', created)"})
            .values("day", "value_type")
            .order_by()
            .annotate(
                average=Avg(
                    Case(
                        When(
                            ~Q(value_type="timestamp"), then=Cast("value", FloatField())
                        ),
                        output_field=FloatField(),
                    )
                )
            )
            .order_by("-day")
        )


class ReadingsNowView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SensorDataValue.objects.none()
    serializer_class = ReadingsNowSerializer

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]

        lte = timezone.now()
        gte = lte - datetime.timedelta(24 * 60)

        return (
            SensorDataValue.objects.filter(
                created__lte=lte,
                created__gte=gte,
                value_type__in=value_types[sensor_type],
            )
            .values("value_type", "sensordata__location__city")
            .order_by()
            .annotate(
                city=F("sensordata__location__city"),
                average=Avg(
                    Case(
                        When(
                            ~Q(value_type="timestamp"), then=Cast("value", FloatField())
                        ),
                        output_field=FloatField(),
                    )
                ),
                min=Min(
                    Case(
                        When(
                            ~Q(value_type="timestamp"), then=Cast("value", FloatField())
                        ),
                        output_field=FloatField(),
                    )
                ),
                max=Max(
                    Case(
                        When(
                            ~Q(value_type="timestamp"), then=Cast("value", FloatField())
                        ),
                        output_field=FloatField(),
                    )
                ),
            )
        )
