from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification
from notifications.services import create_notification

from .models import (
    ProcessStage,
    StudentProcess,
    ProcessStageHistory,
)

from .serializers import (
    ProcessStageSerializer,
    StudentProcessSerializer,
    ProcessStageHistorySerializer,
)

User = get_user_model()


class ProcessStageViewSet(viewsets.ModelViewSet):
    queryset = ProcessStage.objects.all()
    serializer_class = ProcessStageSerializer
    permission_classes = [IsAuthenticated]


class StudentProcessViewSet(viewsets.ModelViewSet):
    queryset = (
        StudentProcess.objects
        .select_related(
            "student",
            "student__user",
            "current_stage",
        )
        .prefetch_related("stage_history")
    )

    serializer_class = StudentProcessSerializer
    permission_classes = [IsAuthenticated]

    # =========================================================
    # COMPLETE CURRENT STAGE
    # =========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="complete-stage",
        permission_classes=[IsAuthenticated],
    )
    def complete_stage(self, request, pk=None):

        user = request.user

        # ---------------------------------------------------------
        # ROLE CHECK
        # ---------------------------------------------------------

        is_staff_process_user = (
            user.is_superuser
            or getattr(user, "role", None)
            in ["admin", "counselor"]
        )

        is_student = (
            getattr(user, "role", None) == "student"
        )

        # Only admin, counselor, superuser and student
        # can complete a process stage.
        if not is_staff_process_user and not is_student:
            return Response(
                {
                    "detail": (
                        "You do not have permission to "
                        "complete process stages."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # =========================================================
        # TRANSACTION
        # =========================================================

        with transaction.atomic():

            # -----------------------------------------------------
            # IMPORTANT:
            # Do NOT use select_related("current_stage")
            # together with select_for_update().
            #
            # current_stage is nullable, and PostgreSQL rejects:
            # FOR UPDATE on the nullable side of an OUTER JOIN.
            #
            # We lock ONLY StudentProcess here.
            # -----------------------------------------------------

            try:
                process = (
                    StudentProcess.objects
                    .select_for_update()
                    .select_related(
                        "student",
                        "student__user",
                    )
                    .get(pk=pk)
                )

            except StudentProcess.DoesNotExist:
                return Response(
                    {
                        "detail": "Student process not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # -----------------------------------------------------
            # ALREADY COMPLETED
            # -----------------------------------------------------

            if getattr(process, "is_completed", False):
                return Response(
                    {
                        "detail": (
                            "This application is already completed."
                        ),
                        "completed": True,
                        "finished": True,
                        "current_stage": None,
                    },
                    status=status.HTTP_200_OK,
                )

            # -----------------------------------------------------
            # CURRENT STAGE
            # -----------------------------------------------------

            current_stage = process.current_stage

            if current_stage is None:
                return Response(
                    {
                        "detail": (
                            "This student does not have "
                            "a current process stage."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # -----------------------------------------------------
            # STUDENT SECURITY
            # -----------------------------------------------------

            if is_student:

                # Student can only complete their own process.
                if process.student.user_id != user.id:
                    return Response(
                        {
                            "detail": (
                                "You cannot complete another "
                                "student's process."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # Students can only complete Steps 1-3.
                if current_stage.order > 3:
                    return Response(
                        {
                            "detail": (
                                "Students can only complete "
                                "Steps 1–3."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # -----------------------------------------------------
            # COMPLETE CURRENT STAGE
            # -----------------------------------------------------

            result = process.complete_current_stage(
                updated_by=user,
                remarks=request.data.get("remarks", ""),
            )

            previous_stage = result.get("previous_stage")
            next_stage = result.get("current_stage")
            finished = result.get("finished", False)

            # Get student user before leaving transaction.
            student_user = process.student.user

        # =========================================================
        # NOTIFICATIONS
        # =========================================================
        #
        # Notification failure should NOT turn a successful
        # process completion into HTTP 500.
        # =========================================================

        try:

            if is_student:

                student_name = (
                    student_user.get_full_name().strip()
                    if hasattr(student_user, "get_full_name")
                    else student_user.email
                )

                admin_users = User.objects.filter(
                    role__in=["admin", "counselor"],
                    is_active=True,
                )

                superusers = User.objects.filter(
                    is_superuser=True,
                    is_active=True,
                )

                admin_users = (
                    admin_users | superusers
                ).distinct()

                if finished:

                    title = "Student Completed Application"

                    message = (
                        f"{student_name} has completed the "
                        "entire application process."
                    )

                    notification_type = (
                        Notification.Type.SUCCESS
                    )

                else:

                    title = (
                        f"Step {previous_stage.order} Completed"
                    )

                    message = (
                        f"{student_name} completed "
                        f"Step {previous_stage.order}: "
                        f"{previous_stage.name}."
                    )

                    notification_type = (
                        Notification.Type.INFO
                    )

                for admin_user in admin_users:

                    try:
                        create_notification(
                            user=admin_user,
                            title=title,
                            message=message,
                            notification_type=notification_type,
                        )
                    except Exception as notification_error:
                        print(
                            "Notification error:",
                            notification_error,
                        )

            else:

                if finished:

                    try:
                        create_notification(
                            user=student_user,
                            title="Application Process Completed",
                            message=(
                                "Congratulations! Your application "
                                "process has been completed."
                            ),
                            notification_type=(
                                Notification.Type.SUCCESS
                            ),
                        )
                    except Exception as notification_error:
                        print(
                            "Notification error:",
                            notification_error,
                        )

                else:

                    try:
                        create_notification(
                            user=student_user,
                            title=(
                                f"Step {previous_stage.order} "
                                "Completed"
                            ),
                            message=(
                                f"Step {previous_stage.order}: "
                                f"{previous_stage.name} has been "
                                "completed. Your next step is "
                                f"Step {next_stage.order}: "
                                f"{next_stage.name}."
                            ),
                            notification_type=(
                                Notification.Type.INFO
                            ),
                        )
                    except Exception as notification_error:
                        print(
                            "Notification error:",
                            notification_error,
                        )

        except Exception as notification_error:

            # Never fail the completed process because of
            # notification/FCM problems.
            print(
                "Process notification error:",
                notification_error,
            )

        # =========================================================
        # RESPONSE
        # =========================================================

        return Response(
            {
                "detail": (
                    "Application process completed."
                    if finished
                    else (
                        f"Step {previous_stage.order} "
                        "completed."
                    )
                ),

                "completed": True,

                "finished": finished,

                "previous_stage": (
                    {
                        "id": previous_stage.id,
                        "name": previous_stage.name,
                        "order": previous_stage.order,
                    }
                    if previous_stage
                    else None
                ),

                "current_stage": (
                    {
                        "id": next_stage.id,
                        "name": next_stage.name,
                        "order": next_stage.order,
                    }
                    if next_stage
                    else None
                ),
            },
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # SET STAGE
    # =========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="set-stage",
        permission_classes=[IsAuthenticated],
    )
    def set_stage(self, request, pk=None):

        user = request.user

        # ---------------------------------------------------------
        # PERMISSION
        # ---------------------------------------------------------

        if not (
            user.is_superuser
            or getattr(user, "role", None)
            in ["admin", "counselor"]
        ):
            return Response(
                {
                    "detail": (
                        "Only admins and counselors can "
                        "change process stages."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ---------------------------------------------------------
        # VALIDATE STAGE ORDER
        # ---------------------------------------------------------

        stage_order = request.data.get("stage_order")

        if stage_order is None:
            return Response(
                {
                    "detail": "stage_order is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            stage_order = int(stage_order)

        except (TypeError, ValueError):
            return Response(
                {
                    "detail": (
                        "stage_order must be an integer."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------
        # LOCK PROCESS
        # ---------------------------------------------------------

        with transaction.atomic():

            try:
                # IMPORTANT:
                # Again, do NOT combine select_for_update()
                # with select_related("current_stage").
                process = (
                    StudentProcess.objects
                    .select_for_update()
                    .select_related(
                        "student",
                        "student__user",
                    )
                    .get(pk=pk)
                )

            except StudentProcess.DoesNotExist:
                return Response(
                    {
                        "detail": "Student process not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # -----------------------------------------------------
            # FIND TARGET STAGE
            # -----------------------------------------------------

            try:
                target_stage = ProcessStage.objects.get(
                    order=stage_order
                )

            except ProcessStage.DoesNotExist:
                return Response(
                    {
                        "detail": (
                            f"Process Stage {stage_order} "
                            "does not exist."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # -----------------------------------------------------
            # CURRENT STAGE
            # -----------------------------------------------------

            previous_stage = process.current_stage

            # -----------------------------------------------------
            # ALREADY ON REQUESTED STAGE
            # -----------------------------------------------------

            if (
                previous_stage is not None
                and previous_stage.id == target_stage.id
            ):
                return Response(
                    {
                        "detail": (
                            f"Student is already on "
                            f"Step {target_stage.order}."
                        ),
                        "current_stage": {
                            "id": target_stage.id,
                            "name": target_stage.name,
                            "order": target_stage.order,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            # -----------------------------------------------------
            # MARK PREVIOUS STAGE COMPLETED
            # -----------------------------------------------------

            if previous_stage is not None:

                previous_history, _ = (
                    ProcessStageHistory.objects
                    .get_or_create(
                        student_process=process,
                        stage=previous_stage,
                        defaults={
                            "status": (
                                ProcessStageHistory
                                .Status.IN_PROGRESS
                            )
                        },
                    )
                )

                previous_history.status = (
                    ProcessStageHistory
                    .Status.COMPLETED
                )

                previous_history.completed_at = timezone.now()

                previous_history.updated_by = user

                previous_history.save(
                    update_fields=[
                        "status",
                        "completed_at",
                        "updated_by",
                    ]
                )

            # -----------------------------------------------------
            # MOVE TO TARGET STAGE
            # -----------------------------------------------------

            process.current_stage = target_stage

            # If your model has is_completed, make sure manually
            # moving to a stage marks it as active again.
            if hasattr(process, "is_completed"):
                process.is_completed = False

                process.save(
                    update_fields=[
                        "current_stage",
                        "is_completed",
                        "updated_at",
                    ]
                )
            else:
                process.save(
                    update_fields=[
                        "current_stage",
                        "updated_at",
                    ]
                )

            # -----------------------------------------------------
            # CREATE / UPDATE TARGET HISTORY
            # -----------------------------------------------------

            ProcessStageHistory.objects.update_or_create(
                student_process=process,
                stage=target_stage,
                defaults={
                    "status": (
                        ProcessStageHistory
                        .Status.IN_PROGRESS
                    ),
                    "updated_by": user,
                },
            )

            # -----------------------------------------------------
            # STUDENT USER
            # -----------------------------------------------------

            student_user = process.student.user

        # =========================================================
        # NOTIFICATION
        # =========================================================

        try:

            create_notification(
                user=student_user,
                title="Application Step Updated",
                message=(
                    f"Your application has been moved "
                    f"to Step {target_stage.order}: "
                    f"{target_stage.name}."
                ),
                notification_type=Notification.Type.INFO,
            )

        except Exception as notification_error:

            print(
                "Set stage notification error:",
                notification_error,
            )

        # =========================================================
        # RESPONSE
        # =========================================================

        return Response(
            {
                "detail": (
                    f"Application moved to "
                    f"Step {target_stage.order}."
                ),

                "previous_stage": (
                    {
                        "id": previous_stage.id,
                        "name": previous_stage.name,
                        "order": previous_stage.order,
                    }
                    if previous_stage
                    else None
                ),

                "current_stage": {
                    "id": target_stage.id,
                    "name": target_stage.name,
                    "order": target_stage.order,
                },

                "finished": False,
            },
            status=status.HTTP_200_OK,
        )


class ProcessStageHistoryViewSet(viewsets.ModelViewSet):

    queryset = (
        ProcessStageHistory.objects
        .select_related(
            "student_process",
            "student_process__student",
            "student_process__student__user",
            "stage",
            "updated_by",
        )
    )

    serializer_class = ProcessStageHistorySerializer
    permission_classes = [IsAuthenticated]