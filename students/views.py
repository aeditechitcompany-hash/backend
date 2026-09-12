from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser,
)

from .models import (
    StudentProfile,
    Education,
    Preferences,
    StudentApplication,
)
from .serializers import (
    StudentProfileSerializer,
    EducationSerializer,
    PreferencesSerializer,
    StudentApplicationSerializer,
    UbtStudentSerializer,
    UbtStudentBasicInfoUpdateSerializer,
)

# ============================================================
# STUDENT APPLICATION
# ============================================================

# ============================================================
# STUDENT PROFILE
# ============================================================

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = (
        StudentProfile.objects
        .select_related(
            "user",
            "country",
            "nationality",
            "assigned_counselor",
            "process",
            "process__current_stage",
        )
        .prefetch_related(
            "education_history",
            "preferences",
            "application",
            "process__stage_history",
        )
        .all()
    )
    serializer_class = StudentProfileSerializer

    filterset_fields = [
        "user",
        "country",
        "nationality",
        "assigned_counselor",
    ]

    search_fields = [
        "user__email",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__phone_number",
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

           # Admins/counselors see students only.
        if (
            user.is_superuser
            or getattr(user, "role", None) in (
                "admin",
                "counselor",
            )
        ):
            return qs.filter(
                user__role="student"
            )
        
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
        url_path="ubt-students",
        permission_classes=[IsAuthenticated],
    )
    def ubt_students(self, request):

        if getattr(request.user, "role", None) != "ubt":
            return Response(
                {
                    "detail": (
                        "Only UBT users can access "
                        "this endpoint."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        students = (
            StudentProfile.objects
            .select_related("user")
            .prefetch_related("application")
            .filter(user__role="student")
            .order_by("-created_at")
        )

        serializer = UbtStudentSerializer(
            students,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["patch"],
        url_path="basic-info",
        permission_classes=[IsAuthenticated],
    )
    def basic_info(self, request, pk=None):

        if getattr(request.user, "role", None) != "ubt":
            return Response(
                {
                    "detail": (
                        "Only UBT users can edit "
                        "student information."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            student = (
                StudentProfile.objects
                .select_related("user")
                .get(
                    pk=pk,
                    user__role="student",
                )
            )

        except StudentProfile.DoesNotExist:
            return Response(
                {
                    "detail": "Student not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = (
            UbtStudentBasicInfoUpdateSerializer(
                student,
                data=request.data,
                partial=True,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            UbtStudentSerializer(
                student,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )


    @action(
        detail=True,
        methods=["post"],
        url_path="set-step",
        permission_classes=[IsAuthenticated],
    )
    def set_step(self, request, pk=None):
        user = request.user

        # Only admins, counselors, and superusers can change
        # a student's application step.
        if not (
            user.is_superuser
            or getattr(user, "role", None) in (
                "admin",
                "counselor",
            )
        ):
            return Response(
                {
                    "detail": "Only admins and counselors can update application steps."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        student = self.get_object()

        try:
            step = int(request.data.get("current_step"))
        except (TypeError, ValueError):
            return Response(
                {
                    "detail": "current_step must be a number from 1 to 10."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if step < 1 or step > 10:
            return Response(
                {
                    "detail": "current_step must be between 1 and 10."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        student.current_step = step
        student.save(
            update_fields=[
                "current_step",
                "updated_at",
            ]
        )

        return Response({
            "detail": "Application step updated successfully.",
            "student_profile_id": str(student.id),
            "user_id": str(student.user.id),
            "current_step": student.current_step,
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

    @action(
        detail=False,
        methods=["get"],
        url_path="ubt-students",
        permission_classes=[IsAuthenticated],
    )
    def ubt_students(self, request):
        if getattr(request.user, "role", None) != "ubt":
            return Response(
                {
                    "detail": "Only UBT users can access this endpoint."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        students = (
            StudentProfile.objects
            .select_related("user")
            .prefetch_related("application")
            .filter(user__role="student")
            .order_by("-created_at")
        )

        return Response(
            UbtStudentSerializer(
                students,
                many=True,
                context={"request": request},
            ).data
        )
    @action(
        detail=True,
        methods=["patch"],
        url_path="basic-info",
        permission_classes=[IsAuthenticated],
    )
    def basic_info(self, request, pk=None):
        if getattr(request.user, "role", None) != "ubt":
            return Response(
                {
                    "detail": "Only UBT users can edit student information."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            student = (
                StudentProfile.objects
                .select_related("user")
                .get(
                    pk=pk,
                    user__role="student",
                )
            )
        except StudentProfile.DoesNotExist:
            return Response(
                {
                    "detail": "Student not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UbtStudentBasicInfoUpdateSerializer(
            student,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        # Return the complete updated UBT student.
        return Response(
            UbtStudentSerializer(
                student,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    # ============================================================
# STUDENT APPLICATION
# ============================================================

# ============================================================
# STUDENT APPLICATION
# ============================================================

class StudentApplicationViewSet(viewsets.ModelViewSet):

    queryset = StudentApplication.objects.select_related(
        "student",
        "student__user",
    ).all()

    serializer_class = StudentApplicationSerializer

    permission_classes = [
        IsAuthenticated,
    ]
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Admins and counselors can access all applications.
        if user.is_superuser or getattr(user, "role", None) in (
            "admin",
            "counselor",
        ):
            return qs

        # Students can only access their own application.
        return qs.filter(
            student__user=user
        )

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):

        try:
            profile = StudentProfile.objects.get(
                user=request.user
            )
        except StudentProfile.DoesNotExist:
            return Response(
                {
                    "detail": "Student profile does not exist."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        application, _ = (
            StudentApplication.objects.get_or_create(
                student=profile
            )
        )

        # ------------------------------------------------------
        # PATCH
        # ------------------------------------------------------

        if request.method == "PATCH":

            serializer = self.get_serializer(
                application,
                data=request.data,
                partial=True,
            )

            serializer.is_valid(
                raise_exception=True
            )

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        # ------------------------------------------------------
        # GET
        # ------------------------------------------------------

        return Response(
            self.get_serializer(application).data,
            status=status.HTTP_200_OK,
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