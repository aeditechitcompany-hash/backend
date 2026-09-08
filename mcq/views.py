from django.db.models import Count, Max, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    QuestionSet,
    Question,
    Option,
    Attempt,
    AttemptAnswer,
)

from .serializers import (
    QuestionSetSerializer,
    QuestionSetDetailSerializer,
    QuestionSetTakeSerializer,
    QuestionSerializer,
    QuestionPublicSerializer,
    OptionSerializer,
    OptionPublicSerializer,
    AttemptSerializer,
    AttemptAnswerSerializer,
    SubmitAnswerSerializer,
    LeaderboardSerializer,
)


# ============================================================================
# HELPERS
# ============================================================================

def _is_staff_role(user):
    """
    Staff users allowed to manage/view all MCQ data.
    """

    return (
        user.is_superuser
        or getattr(user, "role", None) in [
            "admin",
            "counselor",
        ]
    )


def _has_mcq_access(user):
    """
    Check whether the current user has access to the MCQ module.

    Staff users always have access.
    Students need StudentProfile.mcq_access=True.
    """

    if _is_staff_role(user):
        return True
    # UBT users have direct MCQ access.
   
  
    
    try:
        student_profile = user.student_profile
    except Exception:
        return False

    return bool(student_profile.mcq_access)


# ============================================================================
# QUESTION SET VIEWSET
# ============================================================================

class QuestionSetViewSet(viewsets.ModelViewSet):

    queryset = QuestionSet.objects.all()

    permission_classes = [
        IsAuthenticated,
    ]

    # ------------------------------------------------------------------------
    # QUERYSET
    # ------------------------------------------------------------------------

    def get_queryset(self):

        user = self.request.user

        # --------------------------------------------------------------------
        # STAFF
        # --------------------------------------------------------------------

        if _is_staff_role(user):

            return (
                QuestionSet.objects
                .prefetch_related(
                    "questions__options",
                )
                .all()
                .order_by("-created_at")
            )

        # --------------------------------------------------------------------
        # STUDENT
        # --------------------------------------------------------------------

        if not _has_mcq_access(user):
            return QuestionSet.objects.none()

        return (
            QuestionSet.objects
            .filter(
                is_active=True,
            )
            .prefetch_related(
                "questions__options",
            )
            .order_by("-created_at")
        )

    # ------------------------------------------------------------------------
    # SERIALIZER
    # ------------------------------------------------------------------------

    def get_serializer_class(self):

        user = self.request.user

        # Student requesting a specific quiz.
        #
        # This is important:
        #
        # /question-sets/1/
        #
        # must use QuestionSetTakeSerializer for students.
        #

        if self.action == "retrieve":

            if _is_staff_role(user):
                return QuestionSetDetailSerializer

            return QuestionSetTakeSerializer

        return QuestionSetSerializer

    # ------------------------------------------------------------------------
    # CREATE QUESTION SET
    # ------------------------------------------------------------------------

    def perform_create(self, serializer):

        if not _is_staff_role(self.request.user):

            raise PermissionDenied(
                "Only staff users can create question sets."
            )

        serializer.save(
            created_by=self.request.user,
        )

    # ------------------------------------------------------------------------
    # UPDATE QUESTION SET
    # ------------------------------------------------------------------------

    def perform_update(self, serializer):

        if not _is_staff_role(self.request.user):

            raise PermissionDenied(
                "Only staff users can update question sets."
            )

        serializer.save()

    # ------------------------------------------------------------------------
    # DELETE QUESTION SET
    # ------------------------------------------------------------------------

    def perform_destroy(self, instance):

        if not _is_staff_role(self.request.user):

            raise PermissionDenied(
                "Only staff users can delete question sets."
            )

        instance.delete()


# ============================================================================
# QUESTION VIEWSET
# ============================================================================

class QuestionViewSet(viewsets.ModelViewSet):

    queryset = Question.objects.all()

    permission_classes = [
        IsAuthenticated,
    ]

    # ------------------------------------------------------------------------
    # QUERYSET
    # ------------------------------------------------------------------------

    def get_queryset(self):

        user = self.request.user

        # --------------------------------------------------------------------
        # STAFF
        # --------------------------------------------------------------------

        if _is_staff_role(user):

            return (
                Question.objects
                .select_related(
                    "question_set",
                )
                .prefetch_related(
                    "options",
                )
                .all()
                .order_by(
                    "question_set",
                    "order",
                )
            )

        # --------------------------------------------------------------------
        # STUDENT
        # --------------------------------------------------------------------

        if not _has_mcq_access(user):

            return Question.objects.none()

        return (
            Question.objects
            .select_related(
                "question_set",
            )
            .prefetch_related(
                "options",
            )
            .filter(
                question_set__is_active=True,
            )
            .order_by(
                "question_set",
                "order",
            )
        )

    # ------------------------------------------------------------------------
    # SERIALIZER
    # ------------------------------------------------------------------------

    def get_serializer_class(self):

        if _is_staff_role(self.request.user):

            return QuestionSerializer

        return QuestionPublicSerializer

    # ------------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------------

    def perform_create(self, serializer):

        if not _is_staff_role(self.request.user):

            raise PermissionDenied(
                "Only staff users can create questions."
            )

        serializer.save()

    # ------------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------------

    def perform_update(self, serializer):

        if not _is_staff_role(self.request.user):

            raise PermissionDenied(
                "Only staff users can update questions."
            )

        serializer.save()

    # ------------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------------

    def perform_destroy(self, instance):

        if not _is_staff_role(self.request.user):

            raise PermissionDenied(
                "Only staff users can delete questions."
            )

        instance.delete()


# ============================================================================
# OPTION VIEWSET
# ============================================================================

class OptionViewSet(viewsets.ModelViewSet):

    queryset = Option.objects.all()

    permission_classes = [
        IsAuthenticated,
    ]

    # ------------------------------------------------------------------------
    # QUERYSET
    # ------------------------------------------------------------------------

    def get_queryset(self):

        user = self.request.user

        # --------------------------------------------------------------------
        # STAFF
        # --------------------------------------------------------------------

        if _is_staff_role(user):

            return (
                Option.objects
                .select_related(
                    "question",
                    "question__question_set",
                )
                .all()
                .order_by(
                    "question",
                    "order",
                )
            )

        # --------------------------------------------------------------------
        # STUDENT
        # --------------------------------------------------------------------

        if not _has_mcq_access(user):

            return Option.objects.none()

        return (
            Option.objects
            .select_related(
                "question",
                "question__question_set",
            )
            .filter(
                question__question_set__is_active=True,
            )
            .order_by(
                "question",
                "order",
            )
        )

    # ------------------------------------------------------------------------
    # SERIALIZER
    # ------------------------------------------------------------------------

    def get_serializer_class(self):

        if _is_staff_role(self.request.user):

            return OptionSerializer

        return OptionPublicSerializer

    # ------------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------------

    def perform_create(self, serializer):

        if not _is_staff_role(self.request.user):

            raise PermissionDenied(
                "Only staff users can create options."
            )

        serializer.save()

    # ------------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------------

    def perform_update(self, serializer):

        if not _is_staff_role(self.request.user):

            raise PermissionDenied(
                "Only staff users can update options."
            )

        serializer.save()

    # ------------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------------

    def perform_destroy(self, instance):

        if not _is_staff_role(self.request.user):

            raise PermissionDenied(
                "Only staff users can delete options."
            )

        instance.delete()


# ============================================================================
# ATTEMPT VIEWSET
# ============================================================================

class AttemptViewSet(viewsets.ModelViewSet):

    permission_classes = [
        IsAuthenticated,
    ]

    # ------------------------------------------------------------------------
    # QUERYSET
    # ------------------------------------------------------------------------

    def get_queryset(self):

        user = self.request.user

        # --------------------------------------------------------------------
        # STAFF
        # --------------------------------------------------------------------

        if _is_staff_role(user):

            return (
                Attempt.objects
                .select_related(
                    "student__user",
                    "question_set",
                )
                .prefetch_related(
                    "answers__question",
                    "answers__selected_option",
                )
                .all()
                .order_by("-started_at")
            )

        # --------------------------------------------------------------------
        # STUDENT
        # --------------------------------------------------------------------

        if not _has_mcq_access(user):

            return Attempt.objects.none()

        try:
            student_profile = user.student_profile
        except Exception:

            return Attempt.objects.none()

        return (
            Attempt.objects
            .select_related(
                "student__user",
                "question_set",
            )
            .prefetch_related(
                "answers__question",
                "answers__selected_option",
            )
            .filter(
                student=student_profile,
            )
            .order_by("-started_at")
        )

    # ------------------------------------------------------------------------
    # SERIALIZER
    # ------------------------------------------------------------------------

    def get_serializer_class(self):

        if self.action == "submit_answer":

            return SubmitAnswerSerializer

        return AttemptSerializer

    # ------------------------------------------------------------------------
    # CREATE ATTEMPT
    # ------------------------------------------------------------------------

    def perform_create(self, serializer):

        user = self.request.user

        if not _has_mcq_access(user):

            raise PermissionDenied(
                "You do not have access to the MCQ module."
            )

        try:
            student_profile = user.student_profile
        except Exception:

            raise PermissionDenied(
                "Student profile not found."
            )

        question_set = serializer.validated_data[
            "question_set"
        ]

        # Students can only attempt active question sets.

        if (
            not _is_staff_role(user)
            and not question_set.is_active
        ):

            raise ValidationError({
                "question_set":
                    "This question set is not active."
            })

        serializer.save(
            student=student_profile,
        )

    # =========================================================================
    # SUBMIT ANSWER
    # =========================================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="answer",
    )
    def submit_answer(
        self,
        request,
        pk=None,
    ):

        attempt = self.get_object()

        # ---------------------------------------------------------------------
        # ACCESS
        # ---------------------------------------------------------------------

        if not _has_mcq_access(request.user):

            return Response(
                {
                    "detail":
                        "You do not have access to the MCQ module."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ---------------------------------------------------------------------
        # OWNERSHIP
        # ---------------------------------------------------------------------

        if not _is_staff_role(request.user):

            try:
                student_profile = request.user.student_profile
            except Exception:

                return Response(
                    {
                        "detail":
                            "Student profile not found."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if attempt.student_id != student_profile.id:

                return Response(
                    {
                        "detail":
                            "You cannot modify this attempt."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # ---------------------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------------------

        if attempt.status != Attempt.Status.IN_PROGRESS:

            return Response(
                {
                    "detail":
                        "This attempt is no longer active."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------------------
        # VALIDATE
        # ---------------------------------------------------------------------

        serializer = SubmitAnswerSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        question = serializer.validated_data[
            "question"
        ]

        selected_option = serializer.validated_data.get(
            "selected_option",
        )
        print("========================================")
        print("MCQ ANSWER DEBUG")
        print("Attempt:", attempt.id)
        print("Question:", question.id)
        print("Question text:", question.text)
        print("Selected option:", selected_option.id if selected_option else None)
        print(
            "Selected option text:",
            selected_option.text if selected_option else None,
        )
        print(
            "Selected option is_correct:",
            selected_option.is_correct if selected_option else None,
        )

        print("ALL OPTIONS:")
        for option in question.options.all():
            print(
                "  ID:",
                option.id,
                "| TEXT:",
                option.text,
                "| CORRECT:",
                option.is_correct,
                "| ORDER:",
                option.order,
            )

        print("========================================")

        # ---------------------------------------------------------------------
        # QUESTION BELONGS TO QUESTION SET
        # ---------------------------------------------------------------------

        if question.question_set_id != attempt.question_set_id:

            return Response(
                {
                    "detail":
                        "This question does not belong "
                        "to this question set."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------------------
        # OPTION BELONGS TO QUESTION
        # ---------------------------------------------------------------------

        if selected_option is not None:

            if selected_option.question_id != question.id:

                return Response(
                    {
                        "detail":
                            "This option does not belong "
                            "to this question."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ---------------------------------------------------------------------
        # CHECK CORRECTNESS
        # ---------------------------------------------------------------------

        is_correct = (
            selected_option is not None
            and selected_option.is_correct
        )

        # ---------------------------------------------------------------------
        # CREATE / UPDATE ANSWER
        # ---------------------------------------------------------------------

        answer, created = (
            AttemptAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    "selected_option": selected_option,
                    "is_correct": is_correct,
                },
            )
        )

        return Response(
            AttemptAnswerSerializer(answer).data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )

    # =========================================================================
    # FINISH ATTEMPT
    # =========================================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="finish",
    )
    def finish(
        self,
        request,
        pk=None,
    ):

        attempt = self.get_object()

        # ---------------------------------------------------------------------
        # ACCESS
        # ---------------------------------------------------------------------

        if not _has_mcq_access(request.user):

            return Response(
                {
                    "detail":
                        "You do not have access to the MCQ module."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ---------------------------------------------------------------------
        # OWNERSHIP
        # ---------------------------------------------------------------------

        if not _is_staff_role(request.user):

            try:
                student_profile = request.user.student_profile
            except Exception:

                return Response(
                    {
                        "detail":
                            "Student profile not found."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if attempt.student_id != student_profile.id:

                return Response(
                    {
                        "detail":
                            "You cannot finish this attempt."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # ---------------------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------------------

        if attempt.status != Attempt.Status.IN_PROGRESS:

            return Response(
                {
                    "detail":
                        "This attempt has already been completed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------------------
        # FINISH
        # ---------------------------------------------------------------------

        attempt.status = Attempt.Status.SUBMITTED

        attempt.save(
            update_fields=["status"],
        )

        # ---------------------------------------------------------------------
        # GRADE
        # ---------------------------------------------------------------------

        attempt.grade()

        # ---------------------------------------------------------------------
        # QUESTION RESULTS
        # ---------------------------------------------------------------------

        answers = (
            attempt.answers
            .select_related(
                "question",
                "selected_option",
            )
            .all()
            .order_by(
                "question__order",
            )
        )

        question_results = []

        for answer in answers:

            correct_option_id = (
                Option.objects
                .filter(
                    question_id=answer.question_id,
                    is_correct=True,
                )
                .values_list(
                    "id",
                    flat=True,
                )
                .first()
            )

            question_results.append(
                {
                    "question_id": answer.question_id,
                    "selected_option_id": answer.selected_option_id,
                    "correct_option_id": correct_option_id,
                    "is_correct": answer.is_correct,
                }
            )
        # ---------------------------------------------------------------------
        # RESPONSE
        # ---------------------------------------------------------------------

        return Response(
            {
                "attempt":
                    AttemptSerializer(attempt).data,

                "question_results":
                    question_results,
            },
            status=status.HTTP_200_OK,
        )

    # =========================================================================
    # LEADERBOARD
    # =========================================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="leaderboard",
    )
    def leaderboard(
        self,
        request,
    ):

        # ---------------------------------------------------------------------
        # ACCESS
        # ---------------------------------------------------------------------

        if not _has_mcq_access(request.user):

            return Response(
                {
                    "detail":
                        "You do not have access to the MCQ module."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ---------------------------------------------------------------------
        # LEADERBOARD
        #
        # Ranking:
        #
        # 1. Most correctly answered questions
        # 2. Highest best percentage
        # 3. Most completed quizzes
        # 4. Username alphabetically
        # ---------------------------------------------------------------------

        leaderboard = (
            Attempt.objects
            .filter(
                status=Attempt.Status.SUBMITTED,
                student__user__is_active=True,
            )
            .values(
                "student_id",
                "student__user__first_name",
                "student__user__last_name",
                "student__user__username",
                "student__user__email",
            )
            .annotate(
                best_percentage=Max(
                    "percentage",
                ),

                completed_quizzes=Count(
                    "id",
                    distinct=True,
                ),

                questions_solved=Count(
                    "answers",
                    filter=Q(
                        answers__is_correct=True,
                    ),
                    distinct=True,
                ),
            )
            .order_by(
                "-questions_solved",
                "-best_percentage",
                "-completed_quizzes",
                "student__user__username",
            )
        )

        # ---------------------------------------------------------------------
        # FORMAT
        # ---------------------------------------------------------------------

        results = []

        for index, item in enumerate(
            leaderboard,
            start=1,
        ):

            first_name = (
                item[
                    "student__user__first_name"
                ]
                or ""
            )

            last_name = (
                item[
                    "student__user__last_name"
                ]
                or ""
            )

            name = (
                f"{first_name} {last_name}"
                .strip()
            )

            # -----------------------------------------------------------------
            # FALLBACK NAME
            # -----------------------------------------------------------------

            if not name:

                name = (
                    item[
                        "student__user__username"
                    ]
                    or item[
                        "student__user__email"
                    ]
                )

            results.append(
                {
                    "rank": index,

                    "name": name,

                    "email": item[
                        "student__user__email"
                    ],

                    "score":
                        item["best_percentage"]
                        or 0,

                    "completed_quizzes":
                        item["completed_quizzes"],

                    "questions_solved":
                        item["questions_solved"],
                }
            )

        # ---------------------------------------------------------------------
        # SERIALIZE
        # ---------------------------------------------------------------------

        serializer = LeaderboardSerializer(
            results,
            many=True,
        )

        return Response(
            {
                "count": len(results),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )