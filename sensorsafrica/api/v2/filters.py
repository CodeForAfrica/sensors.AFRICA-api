from django.db import models
from django.contrib import auth
import django_filters
from feinstaub.sensors.views import SensorFilter, SensorType, SensorLocation

class CustomSensorFilter(SensorFilter):
    sensor__node__uid = django_filters.CharFilter(method='node_filter', label="Node UID")
    sensor__sensor_type__name = django_filters.ChoiceFilter(
        field_name='sensor__sensor_type__name',
        lookup_expr='exact',
        label="Sensor Type",
        choices=lambda: [(sensor_type.name, sensor_type.name) for sensor_type in SensorType.objects.all()]
    )
    location__country = django_filters.ChoiceFilter(
        field_name='location__country',
        lookup_expr='exact',
        label="Country",
        choices=lambda: list(set([(locale.country, locale.country) for locale in SensorLocation.objects.all()]))
    )
    # sensor__node__owner = django_filters.ModelChoiceFilter(
    #     field_name='sensor__node__owner',
    #     queryset=auth.get_user_model().objects.all(),
    #     label="Owner"
    # )
    sensor__node__owner__username = django_filters.CharFilter(
        field_name='sensor__node__owner__username',
        method="node_owner_filter",
        label="Node owner"
    )

    class Meta(SensorFilter.Meta):
        fields = {
            "sensor__node__uid": ["exact"],
            "sensor__sensor_type__name": ["exact"],
            "sensor__public": ["exact"],
            "location__country": ['exact'],
            "location__city": ['exact'],
            "timestamp": ("gte", "lte"),
            "sensor__node__owner__username": ["exact"], 
        }

        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
            },
        }

    def node_filter(self, queryset, name, value):
        return queryset.filter(**{name: value})

    def node_owner_filter(self,queryset,name,value):
        filtered = queryset.filter(**{name: value})
        return filtered