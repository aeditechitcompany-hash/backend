from rest_framework.routers import DefaultRouter
from .views import VisaApplicationViewSet, VisaDocumentViewSet

router = DefaultRouter()
router.register(r"visa-applications", VisaApplicationViewSet, basename="visa-application")
router.register(r"visa-documents", VisaDocumentViewSet, basename="visa-document")

urlpatterns = router.urls
