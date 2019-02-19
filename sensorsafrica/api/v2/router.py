from rest_framework import routers
from django.conf.urls import url, include

from .views import SensorDataStatView, CityView
from ..v1.router import api_urls

data_router = routers.DefaultRouter()

data_router.register(r"(?P<city_slug>[\w-]+)", SensorDataStatView)
data_router.register(r"", SensorDataStatView)

router = routers.DefaultRouter()

router.register(r"cities", CityView)

api_urls += [
    url(r"(?P<sensor_type>[air]+)/data/", include(data_router.urls)),
    url(r"", include(router.urls)),
]
