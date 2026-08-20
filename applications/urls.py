from rest_framework.routers import DefaultRouter
from .views import ApplicationViewSet, ApplicationStatusHistoryViewSet

router = DefaultRouter()
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"application-status-history", ApplicationStatusHistoryViewSet, basename="application-status-history")

urlpatterns = router.urls
