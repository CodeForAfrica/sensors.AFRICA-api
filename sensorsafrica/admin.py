from django.contrib import admin

from .api.models import SensorDataStat, City

from feinstaub.sensors.admin import (
    SensorLocationAdmin,
    SensorLocation,
    SensorData,
    Node,
)

import timeago
import datetime
import django.utils.timezone


def last_data_received_at(self, obj):
    then = (
        SensorData.objects.filter(location=obj)
        .values_list("timestamp", flat=True)
        .last()
    )
    now = datetime.datetime.now(django.utils.timezone.utc)

    if not then:
        return "Unknown"

    return "( %s ) %s" % (
        timeago.format(then, now),
        SensorData.objects.filter(location=obj)
        .values_list("timestamp", flat=True)
        .last(),
    )


def latitude_and_longitude(self, obj):
    return "%s,%s" % (obj.latitude, obj.longitude)


def node_UID(self, obj):
    return Node.objects.filter(location=obj).values_list("uid", flat=True).first()


SensorLocation._meta.verbose_name_plural = "Sensor Node Locations"
SensorLocationAdmin.list_display = [
    "node_UID",
    "location",
    "city",
    "latitude_and_longitude",
    "last_data_received_at",
]
SensorLocationAdmin.last_data_received_at = last_data_received_at
SensorLocationAdmin.latitude_and_longitude = latitude_and_longitude
SensorLocationAdmin.node_UID = node_UID


@admin.register(SensorDataStat)
class SensorDataStatAdmin(admin.ModelAdmin):
    readonly_fields = [
        "node",
        "sensor",
        "location",
        "city_slug",
        "value_type",
        "average",
        "maximum",
        "minimum",
        "timestamp",
    ]
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
        "timestamp",
        "created",
        "modified",
    ]
    list_filter = ["timestamp", "node", "sensor", "location"]

    def get_actions(self, request):
        actions = super(SensorDataStatAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass

    def delete_model(self, request, obj):
        pass

    def save_related(self, request, form, formsets, change):
        pass


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ["slug", "name", "country"]
    list_display = ["slug", "name", "country", "latitude", "longitude"]
    list_filter = ["name", "country"]
