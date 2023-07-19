# The base version is entirely based on feinstaub
from feinstaub.main.views import UsersView
from feinstaub.sensors.views import (
    SensorView,
    StatisticsView,
    SensorDataView,
)

from .views import (
    FilterView,
    NodeView,
    NowView,
    PostSensorDataView,
    SensorsAfricaSensorDataView,
    VerboseSensorDataView,
)

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"push-sensor-data", PostSensorDataView)
router.register(r"node", NodeView)
router.register(r"sensor", SensorView)
router.register(r"data", VerboseSensorDataView)
router.register(r"statistics", StatisticsView, basename="statistics")
router.register(r"now", NowView)
router.register(r"user", UsersView)
router.register(
    r"sensors/(?P<sensor_id>\d+)", SensorsAfricaSensorDataView, basename="sensors"
)
router.register(r"filter", FilterView, basename="filter")


api_urls = router.urls
