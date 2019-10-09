# The base version is entirely based on feinstaub
from feinstaub.main.views import UsersView
from feinstaub.sensors.views import (
    NodeView,
    NowView,
    PostSensorDataView,
    SensorView,
    StatisticsView,
    SensorDataView,
)

from .views import SensorDataView as SensorsAfricaSensorDataView, FilterView

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"push-sensor-data", PostSensorDataView)
router.register(r"node", NodeView)
router.register(r"sensor", SensorView)
router.register(r"data", SensorDataView)
router.register(r"statistics", StatisticsView, basename="statistics")
router.register(r"now", NowView)
router.register(r"user", UsersView)
router.register(r"sensors/(?P<sensor_id>\d+)",
                SensorsAfricaSensorDataView, basename="sensors")
router.register(r"filter", FilterView, basename="filter")

api_urls = router.urls
