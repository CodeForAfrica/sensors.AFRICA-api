from django.db.models import Avg, F, FloatField, Max, Min
from django.db.models.functions import Cast
from django.utils import timezone
from feinstaub.sensors.models import SensorDataValue
from rest_framework import mixins, pagination, viewsets

from .serializers import ReadingsSerializer

value_types = {"air": ["P1", "P2", "humidity", "temperature"]}


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class ReadingsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SensorDataValue.objects.none()
    serializer_class = ReadingsSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]
        city = self.kwargs["city"]

        from_date = self.request.query_params.get("from", None)
        to_date = self.request.query_params.get("to", None)

        if not from_date:
            from_date = timezone.now().date()

        if not to_date:
            to_date = timezone.now().date()

        types = self.request.query_params.get("type", None)

        filter_value_types = value_types[sensor_type]
        if types:
            filter_value_types = set(types.split(",")) & set(value_types[sensor_type])

        return (
            SensorDataValue.objects.filter(
                sensordata__location__city__iexact=city.replace("-", " "),
                value_type__in=filter_value_types,
                created__date__gte=from_date,
                created__date__lte=to_date,
            )
            .datetimes("created", "day")
            .values("datetimefield", "value_type")
            .order_by()
            .annotate(
                day=F("datetimefield"),
                average=Avg(Cast("value", FloatField())),
                minimum=Min(Cast("value", FloatField())),
                maximum=Max(Cast("value", FloatField())),
            )
            .order_by("-day")
        )
