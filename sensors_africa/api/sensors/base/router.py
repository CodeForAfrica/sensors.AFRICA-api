# The base version is entirely based on feinstaub
from feinstaub.sensors.views import (
    NodeView,
    NowView,
    PostSensorDataView,
    SensorDataView,
    SensorView,
    StatisticsView,
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"push-sensor-data", PostSensorDataView)
router.register(r"node", NodeView)
router.register(r"sensor", SensorView)
router.register(r"data", SensorDataView)
router.register(r"statistics", StatisticsView, basename="statistics")
router.register(r"now", NowView)

api_urls = router.urls
