import datetime
import pytz

from rest_framework.exceptions import ValidationError

from django.utils import timezone
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum
from django.db.models.functions import TruncDate
from rest_framework import mixins, pagination, viewsets

from ..models import SensorDataStat
from .serializers import SensorDataStatSerializer

value_types = {"air": ["P1", "P2", "humidity", "temperature"]}


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


def beginning_of_today():
    return timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_today():
    return beginning_of_today() + datetime.timedelta(hours=24)


def beginning_of_day(from_date):
    return datetime.datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)


def end_of_day(to_date):
    date = datetime.datetime.strptime(to_date, "%Y-%m-%d")
    return (date + datetime.timedelta(hours=24)).replace(tzinfo=pytz.UTC)


def validate_date(date_text, error):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValidationError(error)


class SensorDataStatView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SensorDataStat.objects.none()
    serializer_class = SensorDataStatSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]
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

        return (
            SensorDataStat.objects.filter(
                city_slug=city_slug,
                value_type__in=filter_value_types,
                datehour__gte=from_date,
                datehour__lte=to_date,
            )
            .values("value_type")
            .order_by()
            .annotate(
                average=ExpressionWrapper(
                    Sum(F("average") * F("sample_size")) / Sum("sample_size"),
                    output_field=FloatField(),
                ),
                minimum=Min("minimum"),
                maximum=Max("maximum"),
            )
        )

    @staticmethod
    def _retrieve_range(from_date, to_date, city_slug, filter_value_types):
        if not to_date:
            from_date = beginning_of_day(from_date)
            to_date = end_of_today()
        else:
            from_date = beginning_of_day(from_date)
            to_date = end_of_day(to_date)

        print(SensorDataStat.objects.filter(
                city_slug=city_slug,
                value_type__in=filter_value_types,
                datehour__gte=from_date,
                datehour__lt=to_date,
            )
            .annotate(date=TruncDate("datehour"))
            .values("date", "value_type")
            .annotate(
                average=ExpressionWrapper(
                    Sum(F("average") * F("sample_size")) / Sum("sample_size"),
                    output_field=FloatField(),
                ),
                minimum=Min("minimum"),
                maximum=Max("maximum"),
            )
            .order_by("-date").query)
        return (
            SensorDataStat.objects.filter(
                city_slug=city_slug,
                value_type__in=filter_value_types,
                datehour__gte=from_date,
                datehour__lt=to_date,
            )
            .annotate(date=TruncDate("datehour"))
            .values("date", "value_type")
            .annotate(
                average=ExpressionWrapper(
                    Sum(F("average") * F("sample_size")) / Sum("sample_size"),
                    output_field=FloatField(),
                ),
                minimum=Min("minimum"),
                maximum=Max("maximum"),
            )
            .order_by("-date")
        )
