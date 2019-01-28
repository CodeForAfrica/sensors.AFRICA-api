# The base version is entirely based on feinstaub
from rest_framework import routers

from .views import (
  ReadingsView
)

router = routers.DefaultRouter()
router.register(r'readings', ReadingsView)

api_urls = router.urls
