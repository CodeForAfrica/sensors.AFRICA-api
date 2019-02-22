import django_filters
from django.db import models
from feinstaub.sensors.models import SensorData
from feinstaub.sensors.views import SensorDataView as FeinstaubSensorDataView


class SensorFilter(django_filters.FilterSet):
    class Meta:
        model = SensorData
        fields = {"sensor": ["exact"], "timestamp": ["gte"]}
        filter_overrides = {
             models.DateTimeField: {
                 'filter_class': django_filters.IsoDateTimeFilter,
                 'extra': lambda f: {
                     'lookup_expr': 'gte',
                 },
             },
         }


class SensorDataView(FeinstaubSensorDataView):
    filter_class = SensorFilter
