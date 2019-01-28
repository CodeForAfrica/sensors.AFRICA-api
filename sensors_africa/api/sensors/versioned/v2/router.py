from rest_framework import routers

from ...base.router import api_urls as v1

from .views import (
  SensorsView
)

router = routers.DefaultRouter()

router.register(r'', SensorsView)

api_urls = router.urls + v1
