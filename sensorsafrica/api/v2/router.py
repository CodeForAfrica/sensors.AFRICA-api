from rest_framework import routers
# from django.conf.urls import include, url "django.conf.urls.url() was deprecated in Django 3.0, and is removed in Django 4.0+."
from django.urls import re_path as url, include

from .views import (
    CitiesView,
    NodesView,
    SensorDataStatsView,
    SensorDataView,
    SensorLocationsView,
    SensorTypesView,
    SensorsView,
    meta_data,
)

stat_data_router = routers.DefaultRouter()
stat_data_router.register(r"", SensorDataStatsView)

data_router = routers.DefaultRouter()
data_router.register(r"", SensorDataView)

cities_router = routers.DefaultRouter()
cities_router.register(r"", CitiesView, basename="cities")

nodes_router = routers.DefaultRouter()
nodes_router.register(r"", NodesView, basename="map")

sensors_router = routers.DefaultRouter()
sensors_router.register(r"", SensorsView, basename="sensors")

sensor_locations_router = routers.DefaultRouter()
sensor_locations_router.register(r"", SensorLocationsView, basename="locations")

sensor_types_router = routers.DefaultRouter()
sensor_types_router.register(r"", SensorTypesView, basename="sensor_types")

api_urls = [
    url(r"data/(?P<sensor_type>[air]+)/", include(stat_data_router.urls)),
    url(r"data/", include(data_router.urls)),
    url(r"cities/", include(cities_router.urls)),
    url(r"nodes/", include(nodes_router.urls)),
    url(r"locations/", include(sensor_locations_router.urls)),
    url(r"sensors/", include(sensors_router.urls)),
    url(r"sensor-types/", include(sensor_types_router.urls)),
    url(r"meta/", meta_data),
]
