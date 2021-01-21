import datetime
import pytz
import json


from django.conf import settings
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum, Avg, Q
from django.db.models.functions import Cast, TruncDate
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import mixins, pagination, viewsets
from rest_framework.exceptions import ValidationError

from feinstaub.sensors.models import SensorData
from feinstaub.sensors.serializers import NowSerializer

from .serializers import SensorDataSerializer

class FilterView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SensorDataSerializer

    def get_queryset(self):
        sensor_type = self.request.GET.get("type", r"\w+")
        country = self.request.GET.get("country", r"\w+")
        city = self.request.GET.get("city", r"\w+")
        return (
            SensorData.objects.filter(
                timestamp__gte=timezone.now() - datetime.timedelta(minutes=5),
                sensor__sensor_type__uid__iregex=sensor_type,
                location__country__iregex=country,
                location__city__iregex=city,
            )
            .only("sensor", "timestamp")
            .prefetch_related("sensordatavalues")
        )


class NowView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Show all public sensors active in the last 5 minutes with newest value"""

    permission_classes = []
    serializer_class = NowSerializer
    queryset = SensorData.objects.none()

    def get_queryset(self):
        now = timezone.now()
        startdate = now - datetime.timedelta(minutes=5)
        return SensorData.objects.filter(
            sensor__public=True, modified__range=[startdate, now]
        )


class SensorDataView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SensorDataSerializer

    def get_queryset(self):
        return (
            SensorData.objects.filter(
                timestamp__gte=timezone.now() - datetime.timedelta(minutes=5),
                sensor=self.kwargs["sensor_id"],
            )
            .only("sensor", "timestamp")
            .prefetch_related("sensordatavalues")
        )
