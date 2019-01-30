from rest_framework import routers

from django.conf.urls import include, url

from .views import (
  ReadingsView,
  ReadingsNowView
)

router = routers.DefaultRouter()

router.register(r'now', ReadingsNowView, basename='now')
router.register(r'', ReadingsView)

api_urls = router.urls