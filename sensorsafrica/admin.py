from django.contrib import admin
from django.utils.html import format_html
# from django.conf.urls import include, url "django.conf.urls.url() was deprecated in Django 3.0, and is removed in Django 4.0+."
from django.urls import re_path as url, include
from django.template.response import TemplateResponse
from .api.models import LastActiveNodes, SensorDataStat, City
from django.db.models import Q

from feinstaub.sensors.admin import (
    SensorLocationAdmin,
    SensorLocation,
    SensorData,
    Node,
)

import timeago
import datetime
import django.utils.timezone


@admin.register(LastActiveNodes)
class LastActiveNodesAdmin(admin.ModelAdmin):
    readonly_fields = ["node", "location", "last_data_received_at"]
    list_display = ["node", "location", "received", "previous_locations"]
    search_fields = ["node", "location", "last_data_received_at"]
    list_filter = ["node", "location", "last_data_received_at"]

    def get_queryset(self, request):
        return LastActiveNodes.objects.order_by("node_id").distinct("node_id")

    def received(self, obj):
        now = datetime.datetime.now(django.utils.timezone.utc)

        if not obj.last_data_received_at:
            return "Unknown"

        return "( %s ) %s" % (
            timeago.format(obj.last_data_received_at, now),
            obj.last_data_received_at,
        )

    def previous_locations(self, obj):
        prev = list(
            LastActiveNodes.objects.filter(
                Q(node_id=obj.node), ~Q(location_id=obj.location)
            )
        )
        return format_html(
            """
                <div>
                    <p>
                        <strong>{}</strong>
                    </p>
                    <p>{}</p>
                </div>
            """,
            len(prev),
            ", ".join(map(lambda n: n.location.location, prev))
        )

    def get_actions(self, request):
        actions = super(LastActiveNodesAdmin, self).get_actions(request)
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
