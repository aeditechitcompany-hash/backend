from rest_framework.routers import DefaultRouter
from .views import ProcessStageViewSet, StudentProcessViewSet, ProcessStageHistoryViewSet

router = DefaultRouter()
router.register(r"process-stages", ProcessStageViewSet, basename="process-stage")
router.register(r"student-process", StudentProcessViewSet, basename="student-process")
router.register(r"process-stage-history", ProcessStageHistoryViewSet, basename="process-stage-history")

urlpatterns = router.urls
