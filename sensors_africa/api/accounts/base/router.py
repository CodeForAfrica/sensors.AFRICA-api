from rest_framework import routers

from feinstaub.sensors.views import UsersView

router = routers.DefaultRouter()
router.register(r'user', UsersView)

api_urls = router.urls
