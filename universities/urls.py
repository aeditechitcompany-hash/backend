from rest_framework.routers import DefaultRouter
from .views import UniversityViewSet, CourseViewSet

router = DefaultRouter()
router.register(r"universities", UniversityViewSet, basename="university")
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = router.urls
