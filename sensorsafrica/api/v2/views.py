import datetime
import django_filters
import pytz
import json

from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.db import connection
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum, Avg, Q, Count
from django.db.models.functions import Cast, TruncHour, TruncDay, TruncMonth
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import cache_page

from rest_framework import mixins, pagination, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, authentication_classes

from feinstaub.sensors.views import SensorFilter, StandardResultsSetPagination
from feinstaub.sensors.serializers import NowSerializer
from feinstaub.sensors.models import (
    Node,
    Sensor,
    SensorData,
    SensorDataValue,
    SensorLocation,
    SensorType,
)


from ..models import City, LastActiveNodes, SensorDataStat
from .serializers import (
    SensorDataStatSerializer,
    CitySerializer,
    SensorTypeSerializer,
    NodeSerializer,
    SensorSerializer,
    SensorLocationSerializer,
    SensorDataSerializer,
)

from .filters import CustomSensorFilter

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
        interval = self.request.query_params.get("interval", None)

        results = {}
        for data_stat in data_stats:
            city_slug = data_stat["city_slug"]
            value_type = data_stat["value_type"]

            if city_slug not in results:
                results[city_slug] = {
                    "city_slug": city_slug,
                    value_type: [] if from_date or interval else {},
                }

            if value_type not in results[city_slug]:
                results[city_slug][value_type] = [] if from_date or interval else {}

            values = results[city_slug][value_type]
            include_result = getattr(
                values, "append" if from_date or interval else "update"
            )
            include_result(
                {
                    "average": data_stat["calculated_average"],
                    "minimum": data_stat["calculated_minimum"],
                    "maximum": data_stat["calculated_maximum"],
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


class CitiesView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = StandardResultsSetPagination


class NodesView(viewsets.ViewSet):
    """Create and list nodes, with the option to list authenticated user's nodes."""
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Note: Allow access to list_nodes for https://v2.map.aq.sensors.africa/#4/-4.46/19.54
    @action(detail=False, methods=["get"], url_path="list-nodes", url_name="list_nodes", permission_classes=[AllowAny])
    def list_nodes(self, request):
        """List all public nodes with active sensors."""
        nodes = []
        last_active_nodes = LastActiveNodes.objects.select_related("node", "location").iterator()
        # Loop through the last active nodes
        for last_active in last_active_nodes:
            # Get the current node only if it has public sensors
            node = last_active.node
            if not node.sensors.filter(public=True).exists():
                continue

            # The last acive date
            last_data_received_at = last_active.last_data_received_at

            # last_data_received_at
            stats = []
            # Get data stats from 5mins before last_data_received_at
            if last_data_received_at:
                last_5_mins = last_data_received_at - datetime.timedelta(minutes=5)
                stats = (
                    SensorDataValue.objects.filter(
                        Q(sensordata__sensor__node=node.id),
                        # Open endpoints should return data from public sensors
                        # only in case a node has both public & private sensors
                        Q(sensordata__sensor__public=True),
                        Q(sensordata__location=last_active.location.id),
                        Q(sensordata__timestamp__gte=last_5_mins),
                        Q(sensordata__timestamp__lte=last_data_received_at),
                        # Ignore timestamp values
                        ~Q(value_type="timestamp"),
                        # Match only valid float text
                        Q(value__regex=r"^\-?\d+(\.?\d+)?$"),
                    )
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

            # If the last_active node location is not same as current node location
            # then the node has moved locations since it was last active
            moved_to = None
            if last_active.location.id != node.location.id:
                moved_to = {
                    "name": node.location.location,
                    "longitude": node.location.longitude,
                    "latitude": node.location.latitude,
                    "city": {
                        "name": node.location.city,
                        "slug": slugify(node.location.city),
                    },
                }

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

        return Response(nodes)

    @action(detail=False, methods=["get"], url_path="my-nodes", url_name="my_nodes")
    def list_my_nodes(self, request):
        """List only the nodes owned by the authenticated user."""
        if request.user.is_authenticated:
            queryset = Node.objects.filter(
                Q(owner=request.user)
                | Q(
                    owner__groups__name__in=[
                        g.name for g in request.user.groups.all()
                    ]
                )
            )
            serializer = NodeSerializer(queryset, many=True)
            return Response(serializer.data)
        return Response({"detail": "Authentication credentials were not provided."}, status=403)

    @action(detail=False, methods=["post"], url_path="register-node", url_name="register_node")
    def register_node(self, request):
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class SensorDataPagination(pagination.CursorPagination):
    cursor_query_param = "next_page"
    ordering = "-timestamp"
    page_size = 100


class SensorDataView(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    View for retrieving and downloading detailed sensor data records, with access controlled based on
    user permissions and ownership.

    This endpoint allows authenticated users to retrieve sensor data records, with the following access rules:
    - Users in the `show_me_everything` group have access to all sensor data records.
    - Other users can access data from sensors they own, sensors owned by members of their groups, or public sensors.
    - Non-authenticated users can only access public sensor data.
    """



    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = SensorData.objects.all()
    pagination_class = SensorDataPagination
    permission_classes = [IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = CustomSensorFilter
    serializer_class = SensorDataSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name="show_me_everything").exists():
                return SensorData.objects.all()

            # Return data from sensors owned or
            # owned by someone in the same group as requesting user or
            # public sensors
            return SensorData.objects.filter(
                Q(sensor__node__owner=self.request.user)
                | Q(sensor__node__owner__groups__name__in=[g.name for g in self.request.user.groups.all()])
                | Q(sensor__public=True)
            )

        return SensorData.objects.filter(sensor__public=True)


class SensorDataStatsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    View to retrieve summarized statistics for specific sensor types (e.g., air quality) within a defined date range,
    filtered by city and grouped by specified intervals (hourly, daily, or monthly).

    **URL Parameters:**
        - `sensor_type` (str): The type of sensor data to retrieve (e.g., air_quality).

    **Query Parameters:**
        - `city` (str, optional): Comma-separated list of city slugs to filter data by location.
        - `from` (str, optional): Start date in "YYYY-MM-DD" format. Required if `to` is specified.
        - `to` (str, optional): End date in "YYYY-MM-DD" format. Defaults to 24 hours before `to_date` if unspecified.
        - `interval` (str, optional): Aggregation interval for results - either "hour", "day", or "month". Defaults to "day".
        - `value_type` (str, optional): Comma-separated list of value types to filter (e.g., "PM2.5, PM10").

    **Caching:**
        - Results are cached for 1 hour (`@cache_page(3600)`) to reduce server load.

    **Returns:**
        - A list of sensor data statistics, grouped by city, value type, and specified interval.
        - Each entry includes:
            - `value_type` (str): Type of sensor value (e.g., PM2.5).
            - `city_slug` (str): City identifier.
            - `truncated_timestamp` (datetime): Timestamp truncated to the specified interval.
            - `start_datetime` (datetime): Start of the aggregated time period.
            - `end_datetime` (datetime): End of the aggregated time period.
            - `calculated_average` (float): Weighted average of sensor values.
            - `calculated_minimum` (float): Minimum recorded value within the period.
            - `calculated_maximum` (float): Maximum recorded value within the period.
    """
    queryset = SensorDataStat.objects.none()
    serializer_class = SensorDataStatSerializer
    pagination_class = CustomPagination
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(3600))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        sensor_type = self.kwargs["sensor_type"]

        city_slugs = self.request.query_params.get("city", None)
        from_date = self.request.query_params.get("from", None)
        to_date = self.request.query_params.get("to", None)
        interval = self.request.query_params.get("interval", None)

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
            to_date = timezone.now().replace(minute=0, second=0, microsecond=0)
            from_date = to_date - datetime.timedelta(hours=24)
            interval = "day" if not interval else interval
        elif not to_date:
            from_date = beginning_of_day(from_date)
            # Get data from_date until the end
            # of day yesterday which is the beginning of today
            to_date = beginning_of_today()
        else:
            from_date = beginning_of_day(from_date)
            to_date = end_of_day(to_date)

        queryset = SensorDataStat.objects.filter(
            value_type__in=filter_value_types,
            timestamp__gte=from_date,
            timestamp__lte=to_date,
        )

        if interval == "month":
            truncate = TruncMonth("timestamp")
        elif interval == "day":
            truncate = TruncDay("timestamp")
        else:
            truncate = TruncHour("timestamp")

        if city_slugs:
            queryset = queryset.filter(city_slug__in=city_slugs.split(","))

        return (
            queryset.values("value_type", "city_slug")
            .annotate(
                truncated_timestamp=truncate,
                start_datetime=Min("timestamp"),
                end_datetime=Max("timestamp"),
                calculated_average=ExpressionWrapper(
                    Sum(F("average") * F("sample_size")) / Sum("sample_size"),
                    output_field=FloatField(),
                ),
                calculated_minimum=Min("minimum"),
                calculated_maximum=Max("maximum"),
            )
            .values(
                "value_type",
                "city_slug",
                "truncated_timestamp",
                "start_datetime",
                "end_datetime",
                "calculated_average",
                "calculated_minimum",
                "calculated_maximum",
            )
            .order_by("city_slug", "-truncated_timestamp")
        )


class SensorLocationsView(viewsets.ViewSet):
    """
    View for retrieving and creating sensor entries.
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        queryset = SensorLocation.objects.all()
        serializer = SensorLocationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = SensorLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class SensorTypesView(viewsets.ViewSet):
    """
    View for retrieving and creating sensor type entries.
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        queryset = SensorType.objects.all()
        serializer = SensorTypeSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = SensorTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class SensorsView(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def list(self, request):
        queryset = Sensor.objects.all()
        serializer = SensorSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = SensorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def meta_data(request):
    nodes_count = Node.objects.count()
    sensors_count = Sensor.objects.count()
    sensor_data_count = SensorData.objects.count()

    database_size = get_database_size()
    database_last_updated = get_database_last_updated()
    sensors_countries = get_sensors_countries()
    sensors_cities = get_sensors_cities()

    return Response({
        "sensor_networks": get_sensors_networks(),
        "nodes": {
            "active": get_active_nodes(),
            "count": nodes_count
        },
        "sensors_count": sensors_count,
        "sensor_data_count": sensor_data_count,
        "sensors_countries": sensors_countries,
        "sensors_cities": sensors_cities,
        "database_size": database_size[0],
        "database_last_updated": database_last_updated,
    })

def get_active_nodes():
    nodes_count = Node.objects.filter(last_notify__gte=timezone.now() - datetime.timedelta(days=14)).count()
    return nodes_count

def get_sensors_networks():
    user = User.objects.filter(username=settings.NETWORKS_OWNER).first()
    if user:
        networks = list(user.groups.values_list('name', flat=True))
        networks.append("sensors.AFRICA")
        return {"networks": networks, "count": len(networks)}

def get_sensors_countries():
    sensors_countries = SensorLocation.objects.filter(country__isnull=False).values_list('country', flat=True)
    return sorted(set(sensors_countries))

def get_sensors_cities():
    sensor_cities = Node.objects.filter(location__city__isnull=False).values_list('location__city', flat=True)
    return sorted(set(sensor_cities))

def get_database_size():
    with connection.cursor() as c:
        c.execute(f"SELECT pg_size_pretty(pg_database_size('{connection.settings_dict['NAME']}'))")
        return c.fetchall()

def get_database_last_updated():
    sensor_data_value = SensorDataValue.objects.latest('created')
    if sensor_data_value:
        return sensor_data_value.modified


class NowView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Show all public sensors active in the last 5 minutes with newest value"""

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = NowSerializer

    def get_queryset(self):
        now = timezone.now()
        startdate = now - datetime.timedelta(minutes=5)
        return SensorData.objects.filter(
            sensor__public=True, modified__range=[startdate, now]
        )


class StatisticsView(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user_count = User.objects.aggregate(count=Count('id'))['count']
        sensor_count = Sensor.objects.aggregate(count=Count('id'))['count']
        sensor_data_count = SensorData.objects.aggregate(count=Count('id'))['count']
        sensor_data_value_count = SensorDataValue.objects.aggregate(count=Count('id'))['count']
        sensor_type_count = SensorType.objects.aggregate(count=Count('id'))['count']
        sensor_type_list = list(SensorType.objects.order_by('uid').values_list('name', flat=True))
        location_count = SensorLocation.objects.aggregate(count=Count('id'))['count']

        stats = {
            'user': {
                'count': user_count,
            },
            'sensor': {
                'count': sensor_count,
            },
            'sensor_data': {
                'count': sensor_data_count,
            },
            'sensor_data_value': {
                'count': sensor_data_value_count,
            },
            'sensor_type': {
                'count': sensor_type_count,
                'list': sensor_type_list,
            },
            'location': {
                'count': location_count,
            }
        }
        return Response(stats)
