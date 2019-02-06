from rest_framework import routers

from .views import ReadingsView

router = routers.DefaultRouter()

router.register(r"(?P<city>[\w-]+)", ReadingsView)

api_urls = router.urls
