from django.db import models
import django_filters
from feinstaub.sensors.views import SensorFilter

class CustomSensorFilter(SensorFilter):
    class Meta(SensorFilter.Meta):
        fields = {"sensor": ["exact"],
                    "location__country": ['exact'],
                    "timestamp": ("gte", "lte"),
                }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
            },
        }
