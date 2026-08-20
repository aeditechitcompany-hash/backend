from rest_framework.routers import DefaultRouter
from .views import QuestionSetViewSet, QuestionViewSet, OptionViewSet, AttemptViewSet

router = DefaultRouter()
router.register(r"question-sets", QuestionSetViewSet, basename="question-set")
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"options", OptionViewSet, basename="option")
router.register(r"attempts", AttemptViewSet, basename="attempt")

urlpatterns = router.urls