from django.utils import timezone

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from accounts.permissions import IsCounselor
from students.models import StudentProfile

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
    OptionSerializer,
    AttemptSerializer,
    SubmitAnswerSerializer,
)


# HELPERS

def _is_staff_role(user):
    """
    Returns True for superusers, admins and counselors.
    """

    if not getattr(user, "is_authenticated", False):
        return False

    return (
        user.is_superuser
        or user.role in (
            User.Role.ADMIN,
            User.Role.COUNSELOR,
        )
    )


def _has_mcq_access(user):
    """
    Returns True if the logged-in student has been granted
    MCQ access.

    Admins/counselors/superusers are always allowed.
    """

    if not user or not user.is_authenticated:
        return False

    # Staff can access MCQs regardless of StudentProfile.
    if _is_staff_role(user):
        return True

    try:
        student = StudentProfile.objects.get(user=user)
    except StudentProfile.DoesNotExist:
        return False

    return student.mcq_access


# QUESTION SET VIEWSET

class QuestionSetViewSet(viewsets.ModelViewSet):
    """
    Admin/Counselor:
        Full CRUD access to question sets.

    Student:
        Can only see active question sets when
        StudentProfile.mcq_access=True.
    """

    queryset = QuestionSet.objects.all()

    def get_serializer_class(self):
        # Staff retrieving a question set gets answer keys.
        if self.action == "retrieve":

            if (
                self.request
                and self.request.user.is_authenticated
                and _is_staff_role(self.request.user)
            ):
                return QuestionSetDetailSerializer

            # Students get the public version without answer keys.
            return QuestionSetTakeSerializer

        return QuestionSetSerializer

    def get_queryset(self):
        qs = QuestionSet.objects.all()
        user = self.request.user

        # Not authenticated

        if not user or not user.is_authenticated:
            return qs.none()

        # Admin / Counselor / Superuser

        if _is_staff_role(user):
            return qs

        # Student MCQ access check

        if not _has_mcq_access(user):
            return qs.none()

        # Student with access
        # Only active sets are visible.

        return qs.filter(is_active=True)

    def get_permissions(self):

        # Only counselors can create/update/delete question sets.
        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [IsCounselor()]

        # Everyone else must be authenticated.
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(
        detail=True,
        methods=["get"],
        url_path="take",
    )
    def take(self, request, pk=None):
        """
        Returns the answer-key-free version of a question set.

        A student can only reach this if mcq_access=True because
        get_object() uses get_queryset().
        """

        question_set = self.get_object()

        return Response(
            QuestionSetTakeSerializer(question_set).data
        )


# QUESTION VIEWSET

class QuestionViewSet(viewsets.ModelViewSet):
    """
    Manage individual questions within a question set.
    """

    queryset = (
        Question.objects
        .select_related("question_set")
        .prefetch_related("options")
    )

    serializer_class = QuestionSerializer

    filterset_fields = [
        "question_set",
        "question_type",
    ]

    def get_permissions(self):

        # Only counselors can create/update/delete questions.
        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [IsCounselor()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Prevent students without MCQ access from directly
        requesting questions by question-set ID.
        """

        qs = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return qs.none()

        # Staff can access all questions.
        if _is_staff_role(user):
            return qs

        # Students need MCQ access.
        if not _has_mcq_access(user):
            return qs.none()

        # Students can access questions belonging to active sets.
        return qs.filter(question_set__is_active=True)


# OPTION VIEWSET

class OptionViewSet(viewsets.ModelViewSet):
    """
    Manage answer options.
    """

    queryset = Option.objects.all()

    serializer_class = OptionSerializer

    filterset_fields = [
        "question",
        "is_correct",
    ]

    def get_permissions(self):

        # Only counselors can modify options.
        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [IsCounselor()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Prevent students without MCQ access from directly
        accessing options.
        """

        qs = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return qs.none()

        # Staff can access everything.
        if _is_staff_role(user):
            return qs

        # Student needs MCQ access.
        if not _has_mcq_access(user):
            return qs.none()

        # Only options belonging to active question sets.
        return qs.filter(
            question__question_set__is_active=True
        )


# ATTEMPT VIEWSET

class AttemptViewSet(viewsets.ModelViewSet):
    """
    A student's attempt at a question set.

    Students:
        - Can only see their own attempts.
        - Can only create attempts if mcq_access=True.
        - Cannot access attempts when access is revoked.

    Admins/Counselors:
        - Can see/manage all attempts.
    """

    queryset = (
        Attempt.objects
        .select_related(
            "student__user",
            "question_set",
        )
        .prefetch_related("answers")
    )

    serializer_class = AttemptSerializer

    filterset_fields = [
        "student",
        "question_set",
        "status",
        "passed",
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Admin / Counselor / Superuser

        if _is_staff_role(user):
            return qs

        # Student

        try:
            student = StudentProfile.objects.get(
                user=user
            )
        except StudentProfile.DoesNotExist:
            return qs.none()

        # MCQ access check

        if not student.mcq_access:
            return qs.none()

        # Student can only see own attempts

        return qs.filter(student=student)

    def perform_create(self, serializer):
        user = self.request.user

        # Admin / Counselor / Superuser

        if _is_staff_role(user):
            serializer.save()
            return

        # Student

        try:
            student_profile = StudentProfile.objects.get(
                user=user
            )
        except StudentProfile.DoesNotExist:
            raise PermissionDenied(
                "Student profile does not exist."
            )

        # MCQ ACCESS CHECK

        if not student_profile.mcq_access:
            raise PermissionDenied(
                "MCQ access has not been granted by an administrator."
            )

        # Force the attempt to belong to the logged-in student

        serializer.save(
            student=student_profile
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="answer",
    )
    def submit_answer(self, request, pk=None):
        """
        Submit or update one answer within an in-progress attempt.
        """

        attempt = self.get_object()

        # Check MCQ access again

        if not _is_staff_role(request.user):

            if not attempt.student.user == request.user:
                raise PermissionDenied(
                    "You cannot access this attempt."
                )

            if not attempt.student.mcq_access:
                raise PermissionDenied(
                    "MCQ access has not been granted by an administrator."
                )

        # Attempt must still be in progress

        if attempt.status != Attempt.Status.IN_PROGRESS:
            return Response(
                {
                    "detail": (
                        "This attempt is no longer in progress."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate answer

        serializer = SubmitAnswerSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        question = serializer.validated_data["question"]

        selected_option = serializer.validated_data.get(
            "selected_option"
        )

        # Make sure question belongs to this question set

        if question.question_set_id != attempt.question_set_id:
            return Response(
                {
                    "detail": (
                        "This question does not belong "
                        "to this question set."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Make sure selected option belongs to this question

        if (
            selected_option
            and selected_option.question_id != question.id
        ):
            return Response(
                {
                    "detail": (
                        "The selected option does not "
                        "belong to this question."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save/update answer

        AttemptAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                "selected_option": selected_option
            },
        )

        return Response(
            AttemptSerializer(attempt).data
        )

@action(
    detail=True,
    methods=["post"],
    url_path="finish",
)
def finish(self, request, pk=None):
    """
    Submit the attempt, calculate the final score,
    and return question-by-question review information.
    """

    attempt = self.get_object()

    # --------------------------------------------------
    # CHECK OWNERSHIP / ACCESS
    # --------------------------------------------------

    if not _is_staff_role(request.user):

        if attempt.student.user != request.user:
            raise PermissionDenied(
                "You cannot finish this attempt."
            )

        if not attempt.student.mcq_access:
            raise PermissionDenied(
                "MCQ access has not been granted by an administrator."
            )

    # --------------------------------------------------
    # CHECK IF ALREADY FINISHED
    # --------------------------------------------------

    if attempt.status != Attempt.Status.IN_PROGRESS:
        return Response(
            {
                "detail": "This attempt is already finished."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # MARK ATTEMPT AS SUBMITTED
    # --------------------------------------------------

    attempt.status = Attempt.Status.SUBMITTED
    attempt.submitted_at = timezone.now()

    attempt.save(
        update_fields=[
            "status",
            "submitted_at",
        ]
    )

    # --------------------------------------------------
    # CALCULATE SCORE
    # --------------------------------------------------

    attempt.grade()

    # --------------------------------------------------
    # BUILD REVIEW DATA
    #
    # IMPORTANT:
    # We loop through EVERY question in the question set,
    # not just questions the student answered.
    #
    # This means:
    # - answered correct -> selected + correct
    # - answered wrong   -> selected + correct
    # - unanswered       -> selected = null + correct
    # --------------------------------------------------

    questions = (
        Question.objects
        .filter(question_set=attempt.question_set)
        .prefetch_related("options")
        .order_by("order", "id")
    )

    attempt_answers = (
        AttemptAnswer.objects
        .filter(attempt=attempt)
        .select_related("selected_option")
    )

    answer_map = {
        answer.question_id: answer
        for answer in attempt_answers
    }

    question_results = []

    for question in questions:

        # Find student's answer for this question
        answer = answer_map.get(question.id)

        # Find the correct option
        correct_option = (
            question.options
            .filter(is_correct=True)
            .first()
        )

        selected_option = (
            answer.selected_option
            if answer is not None
            else None
        )

        is_correct = (
            selected_option is not None
            and correct_option is not None
            and selected_option.id == correct_option.id
        )

        question_results.append(
            {
                "question_id": question.id,

                "selected_option_id": (
                    selected_option.id
                    if selected_option is not None
                    else None
                ),

                "correct_option_id": (
                    correct_option.id
                    if correct_option is not None
                    else None
                ),

                "is_correct": is_correct,
            }
        )

    # --------------------------------------------------
    # GET NORMAL ATTEMPT SERIALIZER DATA
    # --------------------------------------------------

    response_data = AttemptSerializer(
        attempt
    ).data

    # Add review information
    response_data["question_results"] = question_results

    # Also explicitly include useful result fields
    response_data["score"] = getattr(
        attempt,
        "score",
        response_data.get("score", 0),
    )

    response_data["max_score"] = response_data.get(
        "max_score",
        getattr(
            attempt,
            "max_score",
            attempt.question_set.question_count,
        ),
    )

    response_data["percentage"] = response_data.get(
        "percentage",
        0,
    )

    response_data["passed"] = response_data.get(
        "passed",
        False,
    )

    return Response(response_data)