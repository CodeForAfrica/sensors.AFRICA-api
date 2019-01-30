from rest_framework import routers

from .views import ReadingsNowView, ReadingsView

router = routers.DefaultRouter()

router.register(r'now', ReadingsNowView, basename='now')
router.register(r'', ReadingsView)

api_urls = router.urls
