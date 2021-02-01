import django_filters

from feinstaub.sensors.models import Node, SensorData

class NodeFilter(django_filters.FilterSet):
    class Meta:
        model = Node
        fields = {
            "location__country": ["iexact"],
            "last_notify": ["gte", "lte"]}
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
                'extra': lambda f: {
                    'lookup_expr': 'gte',
                },
            },
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
                'extra': lambda f: {
                    'lookup_expr': 'lte',
                },
            },
        }


class SensorFilter(django_filters.FilterSet):
    class Meta:
        model = SensorData
        fields = {
            "sensor": ["exact"],
            "timestamp": ["gte", "lte"]
            }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
                'extra': lambda f: {
                    'lookup_expr': 'gte',
                },
            },
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
                'extra': lambda f: {
                    'lookup_expr': 'lte',
                },
            },
        }