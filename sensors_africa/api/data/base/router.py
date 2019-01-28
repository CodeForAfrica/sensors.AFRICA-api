from rest_framework import routers

from .views import (
  ReadingsView,
)

router = routers.DefaultRouter()

router.register(r'', ReadingsView)

api_urls = router.urls