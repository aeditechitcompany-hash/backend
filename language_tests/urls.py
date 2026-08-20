from rest_framework.routers import DefaultRouter
from .views import LanguageTestViewSet

router = DefaultRouter()
router.register(r"language-tests", LanguageTestViewSet, basename="language-test")

urlpatterns = router.urls
