from django.contrib import admin

from .models import SensorDataStat


@admin.register(SensorDataStat)
class SensorDataStatAdmin(admin.ModelAdmin):
    search_fields = ["city_slug", "value_type"]
    list_display = [
        "node",
        "sensor",
        "location",
        "city_slug",
        "value_type",
        "average",
        "maximum",
        "minimum",
        "day",
        "latitude",
        "longitude",
        "created",
        "modified",
    ]
    list_filter = ["day", "node", "sensor", "location"]
