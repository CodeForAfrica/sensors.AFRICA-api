import datetime
import pytz

from rest_framework.exceptions import ValidationError

from django.utils import timezone
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum
from django.db.models.functions import TruncDate
from rest_framework import mixins, pagination, viewsets

from ..models import SensorDataStat, City
from .serializers import SensorDataStatSerializer, CitySerializer

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

    def get_paginated_response(self, data):

        results = {}
        for result in data:
            city_slug = result["city_slug"]
            value_type = result["value_type"]

            if city_slug not in results:
                results[city_slug] = {"city_slug": city_slug, value_type: []}
            if value_type not in results[city_slug]:
                results[city_slug][value_type] = []
            results[city_slug][value_type].append(
                {
                    "average": result["average"],
                    "minimum": result["minimum"],
                    "maximum": result["maximum"],
                    "start_datetime": result["start_datetime"],
                    "end_datetime": result["end_datetime"],
                }
            )

        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": len(results.keys()),
                "results": results.values(),
            }
        )


class SensorDataStatView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SensorDataStat.objects.none()
    serializer_class = SensorDataStatSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]

        city_slug = None
        if "city_slug" in self.kwargs:
            city_slug = self.kwargs["city_slug"]

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
            filter_value_types = set(value_type_to_filter.split(",")) & set(
                value_types[sensor_type]
            )

        if not from_date and not to_date:
            return self._retrieve_past_24hrs(city_slug, filter_value_types)

        return self._retrieve_range(from_date, to_date, city_slug, filter_value_types)

    @staticmethod
    def _retrieve_past_24hrs(city_slug, filter_value_types):
        to_date = timezone.now().replace(minute=0, second=0, microsecond=0)
        from_date = to_date - datetime.timedelta(hours=24)

        queryset = SensorDataStat.objects.filter(
            value_type__in=filter_value_types,
            timestamp__gte=from_date,
            timestamp__lte=to_date,
        )

        if city_slug:
            queryset = queryset.filter(city_slug=city_slug)

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
    def _retrieve_range(from_date, to_date, city_slug, filter_value_types):
        if not to_date:
            from_date = beginning_of_day(from_date)
            to_date = end_of_today()
        else:
            from_date = beginning_of_day(from_date)
            to_date = end_of_day(to_date)

        return (
            SensorDataStat.objects.filter(
                city_slug=city_slug,
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
