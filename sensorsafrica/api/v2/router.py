from rest_framework import routers
from django.conf.urls import url, include

from .views import SensorDataStatView, CityView, NodesView, SensorsLocationView

data_router = routers.DefaultRouter()

data_router.register(r"", SensorDataStatView)

city_router = routers.DefaultRouter()

city_router.register(r"", CityView)

nodes_router = routers.DefaultRouter()

nodes_router.register(r"", NodesView, basename="map")

sensors_location_router = routers.DefaultRouter()
sensors_location_router.register(r"", SensorsLocationView)

api_urls = [
    url(r"data/(?P<sensor_type>[air]+)/", include(data_router.urls)),
    url(r"cities/", include(city_router.urls)),
    url(r"nodes/", include(nodes_router.urls)),
    url(r"locations/", include(sensors_location_router.urls)),
]
