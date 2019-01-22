from rest_framework import routers

from feinstaub.sensors.views import (
    NodeView,
    PostSensorDataView,
    SensorDataView,
    SensorView,
    NowView
)

router = routers.DefaultRouter()
router.register(r'push-sensor-data', PostSensorDataView)
router.register(r'node', NodeView)
router.register(r'sensor', SensorView)
router.register(r'data', SensorDataView)
router.register(r'now', NowView)

api_urls = router.urls
