from rest_framework import routers
from django.conf.urls import url, include

from .views import (
    CitiesView,
    NodesView,
    NowView,
    SensorDataStatsView,
    SensorDataView,
    SensorLocationsView,
    SensorTypesView,
    SensorsView,
    StatisticsView,
    meta_data,
)

router = routers.DefaultRouter()
router.register(r"data", SensorDataView, basename="sensor-data")
router.register(r"data/stats/(?P<sensor_type>[air]+)", SensorDataStatsView, basename="sensor-data-stats")
router.register(r"cities", CitiesView, basename="cities")
router.register(r"nodes", NodesView, basename="nodes")
router.register(r"now", NowView, basename="now")
router.register(r"locations", SensorLocationsView, basename="sensor-locations")
router.register(r"sensors", SensorsView, basename="sensors")
router.register(r"sensor-types", SensorTypesView, basename="sensor-types")
router.register(r"statistics", StatisticsView, basename="statistics")

api_urls = [
    url(r"^", include(router.urls)),
    url(r"^meta/", meta_data),
]
