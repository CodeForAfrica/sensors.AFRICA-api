from rest_framework import routers
from django.conf.urls import url, include

from .views import SensorDataStatView

router = routers.DefaultRouter()

router.register(r"", SensorDataStatView)

api_urls = [
    url(r"(?P<sensor_type>[air]+)/data/(?P<city_slug>[\w-]+)/", include(router.urls))
]
