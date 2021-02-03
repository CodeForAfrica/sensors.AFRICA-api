import datetime
import pytz
import json
import django_filters


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
from feinstaub.sensors.serializers import NowSerializer
from feinstaub.sensors.views import SensorDataView, StandardResultsSetPagination
from feinstaub.sensors.authentication import NodeUidAuthentication

from .filters import NodeFilter, SensorFilter
from .serializers import LastNotifySensorDataSerializer, NodeSerializer, SensorDataSerializer

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
    filter_class = NodeFilter

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


    def add_stat_var_to_nodes(data):
        nodes = []
        for node in data:
            # last data received for this node
            stats = []
            moved_to = None
           
            # Get data stats from 5mins before last_data_received_at
            if node.last_notify:
                last_5_mins = last_notify - datetime.timedelta(minutes=5)
                stats = (
                    SensorDataValue.objects.filter(
                        Q(sensordata__sensor__node=node.id),
                        Q(sensordata__location=node.location.id),
                        Q(sensordata__timestamp__gte=last_5_mins),
                        Q(sensordata__timestamp__lte=node.last_notify),
                        # Ignore timestamp values
                        ~Q(value_type="timestamp"),
                        # Match only valid float text
                        Q(value__regex=r"^\-?\d+(\.?\d+)?$"),
                    )
                    .order_by()
                    .values("value_type")
                    .annotate(
                        sensor_id=F("sensordata__sensor__id"),
                        start_datetime=Min("sensordata__timestamp"),
                        end_datetime=Max("sensordata__timestamp"),
                        average=Avg(Cast("value", FloatField())),
                        minimum=Min(Cast("value", FloatField())),
                        maximum=Max(Cast("value", FloatField())),
                    )
                )

            nodes.append(
                {
                    "node_moved": moved_to is not None,
                    "moved_to": moved_to,
                    "node": {"uid": last_active.node.uid, "id": last_active.node.id, "owner": last_active.node.owner.id},
                    "location": {
                        "name": last_active.location.location,
                        "longitude": last_active.location.longitude,
                        "latitude": last_active.location.latitude,
                        "city": {
                            "name": last_active.location.city,
                            "slug": slugify(last_active.location.city),
                        },
                    },
                    "last_data_received_at": last_data_received_at,
                    "stats": stats,
                }
            )
        return nodes


    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = add_stat_var_to_nodes(serializer.data)
            return self.get_paginated_response(data)
        
        serializer = self.get_serializer(queryset, many=True)
        data = add_stat_var_to_nodes(serializer.data)
        return Response(data)


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

class PostSensorDataView(mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    """ This endpoint is to POST data from the sensor to the api.
    """
    authentication_classes = (NodeUidAuthentication,)
    permission_classes = tuple()
    serializer_class = LastNotifySensorDataSerializer
    queryset = SensorData.objects.all()
    

class VerboseSensorDataView(SensorDataView):
    filter_class = SensorFilter

class SensorsAfricaSensorDataView(mixins.ListModelMixin, viewsets.GenericViewSet):
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

