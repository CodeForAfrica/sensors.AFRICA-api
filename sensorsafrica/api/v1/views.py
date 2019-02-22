import django_filters
from feinstaub.sensors.models import SensorData
from feinstaub.sensors.views import SensorDataView as FeinstaubSensorDataView


class SensorFilter(django_filters.FilterSet):
    class Meta:
        model = SensorData
        fields = {"sensor": ["exact"], "timestamp": ["gte"]}


class SensorDataView(FeinstaubSensorDataView):
    filter_class = SensorFilter
