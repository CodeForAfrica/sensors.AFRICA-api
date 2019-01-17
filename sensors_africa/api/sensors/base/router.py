from rest_framework import routers
from django.conf.urls import include, url

from .views import (
    NodeView,
    PostSensorDataView,
    SensorDataView,
    SensorView,
    NowView,
)

router = routers.DefaultRouter()
router.register(r'push-sensor-data', PostSensorDataView, base_name="push-sensor-data")
router.register(r'node', NodeView)
router.register(r'sensor', SensorView)
router.register(r'data', SensorDataView)
router.register(r'now', NowView)

api_urls = router.urls