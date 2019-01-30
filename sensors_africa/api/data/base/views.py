import datetime

from django.db.models import Avg, Case, FloatField, Max, Min, Q, When
from django.db.models.functions import Cast
from django.utils import timezone
from feinstaub.sensors.models import (SensorData, SensorDataValue,
                                      SensorLocation)
from feinstaub.sensors.serializers import SensorDataValueSerializer
from rest_framework import mixins, viewsets
from rest_framework.response import Response

value_types = {"air": ["P1", "P2"]}


class ReadingsView(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = SensorDataValue.objects.all()
    serializer_class = SensorDataValueSerializer

    def get_queryset(self):
        city = self.request.query_params.get("city")
        if city:
            sensor_data = SensorData.objects.filter(
                location=SensorLocation.objects.get(city=city)
            )
            return SensorDataValue.objects.filter(sensordata__in=sensor_data)
        return SensorDataValue.objects.all()


class ReadingsNowView(viewsets.GenericViewSet):
    def get_stats(self, location, sensor_type):
        sensor_data = SensorData.objects.filter(location=location)

        lte = timezone.now()
        gte = lte - datetime.timedelta(24 * 60)

        stats = {}
        for value_type in value_types[sensor_type]:
            stats[value_type] = (
                SensorDataValue.objects.filter(
                    sensordata__in=sensor_data,
                    created__lte=lte,
                    created__gte=gte,
                    value_type=value_type,
                )
                .annotate(
                    float_value=Case(
                        When(
                            ~Q(value_type="timestamp"),
                            then=Cast("value", FloatField())
                        ),
                        output_field=FloatField(),
                    )
                )
                .aggregate(
                    average=Avg("float_value"),
                    max=Max("float_value"),
                    min=Min("float_value"),
                )
            )

        return stats

    def list(self, request, sensor_type):
        city = request.query_params.get("city")
        if city:
            stats = self.get_stats(SensorLocation.objects.get(city=city), sensor_type)
        else:
            stats = {}
            for location in SensorLocation.objects.all():
                stats[location.city] = self.get_stats(location, sensor_type)
        return Response(stats)
