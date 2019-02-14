from django.contrib import admin

from .models import SensorDataStat


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
