import django_filters

from feinstaub.sensors.models import Node

class NodeFilter(django_filters.FilterSet):
    class Meta:
        model = Node
        fields = {"location__country": ["exact"]}

