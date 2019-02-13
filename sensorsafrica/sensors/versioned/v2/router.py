from rest_framework import routers

from .views import SensorDataStatView
from ...base.router import api_urls

router = routers.DefaultRouter()

router.register(r"(?P<sensor_type>[air]+)/data/(?P<city_slug>[\w-]+)", SensorDataStatView)

api_urls += router.urls
