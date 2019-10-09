import datetime
import pytz
import json

from rest_framework.exceptions import ValidationError

from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum, Avg, Q
from django.db.models.functions import Cast, TruncDate
from rest_framework import mixins, pagination, viewsets

from .serializers import SensorDataSerializer
from feinstaub.sensors.models import SensorData


class SensorDataView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SensorDataSerializer

    def get_queryset(self):
        return (
            SensorData.objects
            .filter(
                timestamp__gte=timezone.now() - datetime.timedelta(minutes=5),
                sensor=self.kwargs["sensor_id"]
            )
            .only('sensor', 'timestamp')
            .prefetch_related('sensordatavalues')
        )


class FilterView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SensorDataSerializer

    def get_queryset(self):
        sensor_type = self.request.GET.get('type', r'\w+')
        country = self.request.GET.get('country', r'\w+')
        city = self.request.GET.get('city', r'\w+')
        return (
            SensorData.objects
            .filter(
                timestamp__gte=timezone.now() - datetime.timedelta(minutes=5),
                sensor__sensor_type__uid__iregex=sensor_type,
                location__country__iregex=country,
                location__city__iregex=city
            )
            .only('sensor', 'timestamp')
            .prefetch_related('sensordatavalues')
        )
