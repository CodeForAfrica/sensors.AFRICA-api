import datetime
import pytz
import json
import django_filters


from django.conf import settings
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum, Avg, Q
from django.db.models.functions import Cast, TruncDate
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import mixins, pagination, viewsets, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response

from feinstaub.sensors.models import Node, SensorData
from feinstaub.sensors.serializers import NowSerializer
from feinstaub.sensors.views import SensorDataView, StandardResultsSetPagination
from feinstaub.sensors.authentication import NodeUidAuthentication

from .filters import NodeFilter, SensorFilter
from .serializers import LastNotifySensorDataSerializer, NodeSerializer, SensorDataSerializer, UserSerializer

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
    queryset = Node.objects.none()
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

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User,email=request.data['email'])
    if not user.check_password(request.data['password']):
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key,'user': serializer.data})