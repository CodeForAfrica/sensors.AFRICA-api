import datetime

from django.db.models import Avg, Max, Min
from rest_framework import mixins, pagination, viewsets

from ..models import SensorDataStat
from .serializers import ReadingsSerializer

value_types = {"air": ["P1", "P2", "humidity", "temperature"]}


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class ReadingsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SensorDataStat.objects.none()
    serializer_class = ReadingsSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]
        city = self.kwargs["city"]

        from_date = self.request.query_params.get("from", None)
        to_date = self.request.query_params.get("to", None)

        if not from_date:
            from_date = str(datetime.date.today())

        if not to_date:
            to_date = str(datetime.date.today())

        types = self.request.query_params.get("type", None)

        filter_value_types = value_types[sensor_type]
        if types:
            filter_value_types = set(types.split(",")) & set(value_types[sensor_type])

        return (
            SensorDataStat.objects.filter(
                city_slug=city,
                value_type__in=filter_value_types,
                day__gte=from_date,
                day__lte=to_date,
            )
            .values("day", "value_type")
            .order_by()
            .annotate(
                average=Avg("average"), minimum=Min("minimum"), maximum=Max("maximum")
            )
            .order_by("-day")
        )
