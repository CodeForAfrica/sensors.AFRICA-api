from rest_framework import routers

from .views import ReadingsView
from ...base.router import api_urls

router = routers.DefaultRouter()

router.register(r"(?P<sensor_type>[air]+)/readings/(?P<city>[\w-]+)", ReadingsView)

api_urls += router.urls
