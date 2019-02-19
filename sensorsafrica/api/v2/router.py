from rest_framework import routers
from django.conf.urls import url, include

from .views import SensorDataStatView, CityView
from ..v1.router import api_urls

data_router = routers.DefaultRouter()

data_router.register(r"", SensorDataStatView)

city_router = routers.DefaultRouter()

city_router.register(r"", CityView)

api_urls = [
    url(r"data/(?P<sensor_type>[air]+)/", include(data_router.urls)),
    url(r"cities/", include(city_router.urls)),
] + api_urls
