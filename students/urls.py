from rest_framework.routers import DefaultRouter

from .views import (
    StudentProfileViewSet,
    EducationViewSet,
    PreferencesViewSet,
    StudentApplicationViewSet,
)


router = DefaultRouter()

router.register(
    r"profiles",
    StudentProfileViewSet,
    basename="student-profile",
)

router.register(
    r"applications",
    StudentApplicationViewSet,
    basename="student-application",
)

router.register(
    r"education",
    EducationViewSet,
    basename="education",
)

router.register(
    r"preferences",
    PreferencesViewSet,
    basename="preferences",
)




urlpatterns = router.urls