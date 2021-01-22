import datetime
import pytz
import json


from django.conf import settings
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum, Avg, Q
from django.db.models.functions import Cast, TruncDate
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import mixins, pagination, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from feinstaub.sensors.models import Node, SensorData
from feinstaub.sensors.serializers import NodeSerializer, NowSerializer
from feinstaub.sensors.views import StandardResultsSetPagination

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


class NodeView(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Show all nodes belonging to authenticated user"""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = SensorData.objects.none()
    serializer_class = NodeSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated():
            if self.request.user.groups.filter(name="show_me_everything").exists():
                return Node.objects.all()

            return Node.objects.filter(
                Q(owner=self.request.user)
                | Q(
                    owner__groups__name__in=[
                        g.name for g in self.request.user.groups.all()
                    ]
                )
            )

        return Node.objects.none()


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
