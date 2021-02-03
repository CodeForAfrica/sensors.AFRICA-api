import django_filters
from django.db import models

from feinstaub.sensors.models import Node, SensorData

class NodeFilter(django_filters.FilterSet):
    class Meta:
        model = Node
        fields = {
            "location__country": ["exact"],
            "location__city": ["exact"],
            "last_notify": ["exact", "gte", "lte"]}
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
            },
        }


class SensorFilter(django_filters.FilterSet):
    class Meta:
        model = SensorData
        fields = {
            "sensor": ["exact"],
            "timestamp": ["exact", "gte", "lte"]
            }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
            },
        }
