from django.db import models
import django_filters
from feinstaub.sensors.views import SensorFilter

class CustomSensorFilter(SensorFilter):
    class Meta(SensorFilter.Meta):
        fields = {"sensor": ["exact"],
                    "sensor__public": ["exact"],
                    "location__country": ['exact'],
                    "location__city": ['exact'],
                    "timestamp": ("gte", "lte"),
                }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
            },
        }
