from django.contrib import admin

from .api.models import SensorDataStat, City

from feinstaub.sensors.admin import SensorLocationAdmin, SensorLocation, SensorData

import timeago
import datetime
import django.utils.timezone


def last_pushed(self, obj):
    then = (
        SensorData.objects.filter(location=obj)
        .values_list("timestamp", flat=True)
        .last()
    )
    now = datetime.datetime.now(django.utils.timezone.utc)

    if not then:
        return "Unknown"

    return "%s ( %s )" % (
        SensorData.objects.filter(location=obj)
        .values_list("timestamp", flat=True)
        .last(),
        timeago.format(then, now),
    )


def geo(self, obj):
    return "%s,%s" % (obj.latitude, obj.longitude)


SensorLocation._meta.verbose_name_plural = "Sensor Node Locations"
SensorLocationAdmin.list_display = ["location", "city", "last_pushed", "geo"]
SensorLocationAdmin.last_pushed = last_pushed
SensorLocationAdmin.geo = geo


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
