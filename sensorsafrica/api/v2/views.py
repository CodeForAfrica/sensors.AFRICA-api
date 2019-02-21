import datetime
import pytz

from rest_framework.exceptions import ValidationError

from django.utils import timezone
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum
from django.db.models.functions import TruncDate
from rest_framework import mixins, pagination, viewsets

from ..models import SensorDataStat, City
from .serializers import SensorDataStatSerializer, CitySerializer

from feinstaub.sensors.views import StandardResultsSetPagination

from rest_framework.response import Response

value_types = {"air": ["P1", "P2", "humidity", "temperature"]}


def beginning_of_today():
    return timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_today():
    return beginning_of_today() + datetime.timedelta(hours=24)


def beginning_of_day(from_date):
    return datetime.datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)


def end_of_day(to_date):
    return beginning_of_day(to_date) + datetime.timedelta(hours=24)


def validate_date(date_text, error):
    try:
        datetime.datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(error)


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 1000
    page_size = 100

    def get_paginated_response(self, data_stats):
        # If filtering from a date
        # We will need to have a list of the value_types e.g. { 'P1': [{}, {}] }
        from_date = self.request.query_params.get("from", None)

        results = {}
        for data_stat in data_stats:
            city_slug = data_stat["city_slug"]
            value_type = data_stat["value_type"]

            if city_slug not in results:
                results[city_slug] = {
                    "city_slug": city_slug,
                    value_type: [] if from_date else {},
                }

            if value_type not in results[city_slug]:
                results[city_slug][value_type] = [] if from_date else {}

            values = results[city_slug][value_type]
            include_result = getattr(values, "append" if from_date else "update")
            include_result(
                {
                    "average": data_stat["average"],
                    "minimum": data_stat["minimum"],
                    "maximum": data_stat["maximum"],
                    "start_datetime": data_stat["start_datetime"],
                    "end_datetime": data_stat["end_datetime"],
                }
            )

        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": len(results.keys()),
                "results": list(results.values()),
            }
        )


class SensorDataStatView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SensorDataStat.objects.none()
    serializer_class = SensorDataStatSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]

        city_slugs = self.request.query_params.get("city", None)
        from_date = self.request.query_params.get("from", None)
        to_date = self.request.query_params.get("to", None)

        if to_date and not from_date:
            raise ValidationError({"from": "Must be provide along with to query"})
        if from_date:
            validate_date(from_date, {"from": "Must be a date in the format Y-m-d."})
        if to_date:
            validate_date(to_date, {"to": "Must be a date in the format Y-m-d."})

        value_type_to_filter = self.request.query_params.get("value_type", None)

        filter_value_types = value_types[sensor_type]
        if value_type_to_filter:
            filter_value_types = set(value_type_to_filter.upper().split(",")) & set(
                [x.upper() for x in value_types[sensor_type]]
            )

        if not from_date and not to_date:
            return self._retrieve_past_24hrs(city_slugs, filter_value_types)

        return self._retrieve_range(from_date, to_date, city_slugs, filter_value_types)

    @staticmethod
    def _retrieve_past_24hrs(city_slugs, filter_value_types):
        to_date = timezone.now().replace(minute=0, second=0, microsecond=0)
        from_date = to_date - datetime.timedelta(hours=24)

        queryset = SensorDataStat.objects.filter(
            value_type__in=filter_value_types,
            timestamp__gte=from_date,
            timestamp__lte=to_date,
        )

        if city_slugs:
            queryset = queryset.filter(city_slug__in=city_slugs.split(','))

        return (
            queryset.order_by()
            .values("value_type", "city_slug")
            .annotate(
                start_datetime=Min("timestamp"),
                end_datetime=Max("timestamp"),
                average=ExpressionWrapper(
                    Sum(F("average") * F("sample_size")) / Sum("sample_size"),
                    output_field=FloatField(),
                ),
                minimum=Min("minimum"),
                maximum=Max("maximum"),
            )
            .order_by("city_slug")
        )

    @staticmethod
    def _retrieve_range(from_date, to_date, city_slugs, filter_value_types):
        if not to_date:
            from_date = beginning_of_day(from_date)
            to_date = end_of_today()
        else:
            from_date = beginning_of_day(from_date)
            to_date = end_of_day(to_date)

        return (
            SensorDataStat.objects.filter(
                city_slug__in=city_slugs.split(','),
                value_type__in=filter_value_types,
                timestamp__gte=from_date,
                timestamp__lt=to_date,
            )
            .annotate(date=TruncDate("timestamp"))
            .values("date", "value_type")
            .annotate(
                city_slug=F("city_slug"),
                start_datetime=Min("timestamp"),
                end_datetime=Max("timestamp"),
                average=ExpressionWrapper(
                    Sum(F("average") * F("sample_size")) / Sum("sample_size"),
                    output_field=FloatField(),
                ),
                minimum=Min("minimum"),
                maximum=Max("maximum"),
            )
            .order_by("-date")
        )


class CityView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = StandardResultsSetPagination
