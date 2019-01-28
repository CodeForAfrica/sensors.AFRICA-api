from rest_framework import routers

from feinstaub.main.views import (
  UsersView
)

router = routers.DefaultRouter()
router.register(r'user', UsersView)

api_urls = router.urls
