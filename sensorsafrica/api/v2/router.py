from rest_framework import routers
from django.conf.urls import url, include

from .views import SensorDataStatView
from ..v1.router import api_urls

router = routers.DefaultRouter()

router.register(r"(?P<city_slug>[\w-]+)", SensorDataStatView)
router.register(r"", SensorDataStatView)

api_urls += [
    url(r"(?P<sensor_type>[air]+)/data/", include(router.urls))
]
