import datetime

import django_filters
from django.db.models import Avg, Case, F, FloatField, Max, Min, Q, When
from django.db.models.functions import Cast
from django.utils import timezone
from feinstaub.sensors.models import SensorData, SensorDataValue
from rest_framework import mixins, viewsets

from .serializers import ReadingsNowSerializer, ReadingsSerializer

value_types = {"air": ["P1", "P2"]}


class ReadingsFilter(django_filters.FilterSet):
    class Meta:
        model = SensorDataValue
        fields = {"created": ["date__range"]}


class ReadingsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SensorDataValue.objects.none()
    serializer_class = ReadingsSerializer

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = ReadingsFilter

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]
        city = self.request.query_params.get("city", None)

        sensordata = SensorData.objects.filter(location__city=city)

        return (
            SensorDataValue.objects.filter(
                sensordata__in=sensordata, value_type__in=value_types[sensor_type]
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
        city = self.request.query_params.get("city", None)

        if city is not None:
            queryset = SensorDataValue.objects.filter(sensordata__location__city=city)
        else:
            queryset = SensorDataValue.objects.filter()

        now = timezone.now()
        prev = now - datetime.timedelta(hours=24)

        return (
            queryset.filter(
                created__range=[prev, now], value_type__in=value_types[sensor_type]
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
