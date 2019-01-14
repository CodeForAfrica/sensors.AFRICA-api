from rest_framework import routers
from django.conf.urls import include, url

from .views import (
  UsersView
)

router = routers.DefaultRouter()
router.register(r'user', UsersView)

api_urls = router.urls