from rest_framework import routers
from django.conf.urls import url, include

from .views import SensorDataStatView, CityView, NodesView

data_router = routers.DefaultRouter()

data_router.register(r"", SensorDataStatView, basename="sensor_data_stat_view")

city_router = routers.DefaultRouter()

city_router.register(r"", CityView)

nodes_router = routers.DefaultRouter()

nodes_router.register(r"", NodesView, basename="map")

api_urls = [
    url(r"data/(?P<sensor_type>[air]+)/", include(data_router.urls)),
    url(r"cities/", include(city_router.urls)),
    url(r"nodes/", include(nodes_router.urls))
]
