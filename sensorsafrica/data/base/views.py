import datetime

from django.db.models import Avg, Max, Min
from rest_framework import mixins, pagination, viewsets

from ..models import SensorDataStat
from .serializers import SensorDataStatSerializer

value_types = {"air": ["P1", "P2", "humidity", "temperature"]}


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class SensorDataStatView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SensorDataStat.objects.none()
    serializer_class = SensorDataStatSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]
        city_slug = self.kwargs["city_slug"]

        from_date = self.request.query_params.get("from", None)
        to_date = self.request.query_params.get("to", None)

        if not from_date:
            from_date = str(datetime.date.today())

        if not to_date:
            to_date = str(datetime.date.today())

        value_type_to_filter = self.request.query_params.get("value_type", None)

        filter_value_types = value_types[sensor_type]
        if value_type_to_filter:
            filter_value_types = set(value_type_to_filter.split(",")) & set(
                value_types[sensor_type]
            )

        return (
            SensorDataStat.objects.filter(
                city_slug=city_slug,
                value_type__in=filter_value_types,
                date__gte=from_date,
                date__lte=to_date,
            )
            .values("date", "value_type")
            .order_by()
            .annotate(
                average=Avg("average"), minimum=Min("minimum"), maximum=Max("maximum")
            )
            .order_by("-date")
        )
