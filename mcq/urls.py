from rest_framework.routers import DefaultRouter

from .views import (
    QuestionSetViewSet,
    QuestionViewSet,
    OptionViewSet,
    AttemptViewSet,
    MCQImportViewSet,
    ImportedQuestionReviewViewSet,
    ImportedOptionReviewViewSet,
)


router = DefaultRouter()

router.register(
    r"question-sets",
    QuestionSetViewSet,
    basename="question-set",
)

router.register(
    r"questions",
    QuestionViewSet,
    basename="question",
)

router.register(
    r"options",
    OptionViewSet,
    basename="option",
)

router.register(
    r"attempts",
    AttemptViewSet,
    basename="attempt",
)

router.register(
    r"imports",
    MCQImportViewSet,
    basename="mcq-import",
)  

router.register(
    r"imported-questions",
    ImportedQuestionReviewViewSet,
    basename="imported-question-review",
)

router.register(
    r"imported-options",
    ImportedOptionReviewViewSet,
    basename="imported-option-review",
)


urlpatterns = router.urls