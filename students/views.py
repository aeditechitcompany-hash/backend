from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import StudentProfile, Education, Preferences
from .serializers import (
    StudentProfileSerializer,
    EducationSerializer,
    PreferencesSerializer,
)


# ============================================================
# STUDENT PROFILE
# ============================================================

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.select_related(
        "user",
        "country",
        "nationality",
    ).all()

    serializer_class = StudentProfileSerializer

    filterset_fields = [
        "user",
        "country",
        "nationality",
        "assigned_counselor",
    ]

    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_superuser or getattr(user, "role", None) in (
            "admin",
            "counselor",
        ):
            return qs

        return qs.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user

        if getattr(user, "role", None) == "student":
            serializer.save(user=user)
        else:
            serializer.save()

    @action(
        detail=True,
        methods=["post"],
        url_path="grant-mcq-access",
    )
    def grant_mcq_access(self, request, pk=None):
        user = request.user

        if not (
            user.is_superuser
            or getattr(user, "role", None) == "admin"
        ):
            return Response(
                {"detail": "Only admins can grant MCQ access."},
                status=403,
            )

        student = self.get_object()

        student.mcq_access = True
        student.save(update_fields=["mcq_access"])

        return Response({
            "detail": "MCQ access granted successfully.",
            "student_profile_id": str(student.id),
            "user_id": str(student.user.id),
            "mcq_access": student.mcq_access,
        })

    @action(
        detail=False,
        methods=["get"],
        url_path="my-mcq-access",
        permission_classes=[IsAuthenticated],
    )
    def my_mcq_access(self, request):
        """
        Returns access status for the logged-in student.
        """

        try:
            profile = StudentProfile.objects.get(
                user=request.user
            )
        except StudentProfile.DoesNotExist:
            return Response(
                {
                    "mcq_access": False,
                    "book_access": False,
                    "detail": "Student profile not found.",
                },
                status=404,
            )

        return Response({
            "mcq_access": profile.mcq_access,
            "book_access": profile.book_access,
        })

    @action(
    detail=False,
    methods=["get"],
    url_path="me",
    permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """
         Return the logged-in student's profile.
         Used by Flutter to check MCQ access.
        """
        try:
           profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
           return Response(
            {"detail": "Student profile does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )

        return Response(
        StudentProfileSerializer(profile).data
    )

# ============================================================
# EDUCATION
# ============================================================

class EducationViewSet(viewsets.ModelViewSet):

    queryset = Education.objects.select_related(
        "student",
        "student__user",
        "country",
    ).all()

    serializer_class = EducationSerializer

    filterset_fields = [
        "student",
        "degree_level",
        "country",
        "passout_year",
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Admins/counselors can see all education records.
        if user.is_superuser or getattr(user, "role", None) in (
            "admin",
            "counselor",
        ):
            return qs

        # Students can only access their own education records.
        return qs.filter(
            student__user=user
        )

    def perform_create(self, serializer):

        user = self.request.user

        # Student submits their own academic details.
        if getattr(user, "role", None) == "student":

            profile, _ = StudentProfile.objects.get_or_create(
                user=user
            )

            # Update existing education record instead of
            # creating duplicate records.
            education = Education.objects.filter(
                student=profile
            ).first()

            if education:
                serializer.instance = education
                serializer.save(
                    student=profile
                )
            else:
                serializer.save(
                    student=profile
                )

        else:
            serializer.save()

    # ========================================================
    # ACADEMIC DETAILS STATUS
    # ========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="my-status",
        permission_classes=[IsAuthenticated],
    )
    def my_status(self, request):

        try:
            profile = StudentProfile.objects.get(
                user=request.user
            )

        except StudentProfile.DoesNotExist:

            return Response({
                "has_academic_details": False,
                "student_profile_id": None,
                "education": [],
            })

        education = Education.objects.filter(
            student=profile
        ).order_by(
            "-passout_year",
            "-end_date",
        )

        return Response({
            "has_academic_details": education.exists(),
            "student_profile_id": str(profile.id),
            "education": EducationSerializer(
                education,
                many=True,
            ).data,
        })


# ============================================================
# PREFERENCES
# ============================================================

class PreferencesViewSet(viewsets.ModelViewSet):

    queryset = Preferences.objects.all()

    serializer_class = PreferencesSerializer

    filterset_fields = [
        "student",
        "preferred_study_level",
    ]