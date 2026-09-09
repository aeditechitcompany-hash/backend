from django.db import transaction
from django.utils import timezone

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

        # -----------------------------------------------------
        # ROLE CHECK
        # -----------------------------------------------------

        is_staff_process_user = (
            user.is_superuser
            or getattr(user, "role", None) in [
                "admin",
                "counselor",
            ]
        )

        is_student = (
            getattr(user, "role", None) == "student"
        )

        # Only admin, counselor, superuser and student
        # are allowed to complete stages.
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

        # -----------------------------------------------------
        # LOCK PROCESS
        # -----------------------------------------------------

        with transaction.atomic():

            try:
                process = (
                    StudentProcess.objects
                    .select_for_update()
                    .select_related(
                        "student",
                        "student__user",
                        "current_stage",
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

            # -------------------------------------------------
            # CURRENT STAGE CHECK
            # -------------------------------------------------

            if process.current_stage is None:
                return Response(
                    {
                        "detail": (
                            "This student does not have "
                            "a current process stage."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            current_stage = process.current_stage
            current_order = current_stage.order

            # -------------------------------------------------
            # STUDENT SECURITY
            # -------------------------------------------------

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

                # Student can only complete Steps 1-3.
                if current_order > 3:
                    return Response(
                        {
                            "detail": (
                                "Students can only complete "
                                "Steps 1–3."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # -------------------------------------------------
            # COMPLETE CURRENT STAGE
            # -------------------------------------------------

            result = process.complete_current_stage(
                updated_by=user,
            )

            previous_stage = result["previous_stage"]
            next_stage = result["current_stage"]
            finished = result["finished"]

            # -------------------------------------------------
            # STUDENT USER
            # -------------------------------------------------

            student_user = process.student.user

            # -------------------------------------------------
            # NOTIFICATION
            # -------------------------------------------------

            if finished:

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

            else:

                create_notification(
                    user=student_user,
                    title=(
                        f"Step {previous_stage.order} "
                        f"Completed"
                    ),
                    message=(
                        f"Step {previous_stage.order}: "
                        f"{previous_stage.name} has been "
                        f"completed. Your next step is "
                        f"Step {next_stage.order}: "
                        f"{next_stage.name}."
                    ),
                    notification_type=(
                        Notification.Type.INFO
                    ),
                )

            # -------------------------------------------------
            # RESPONSE
            # -------------------------------------------------

            return Response(
                {
                    "detail": (
                        f"Step {previous_stage.order} "
                        f"completed successfully."
                    ),
                    "previous_stage": {
                        "id": previous_stage.id,
                        "name": previous_stage.name,
                        "order": previous_stage.order,
                    },
                    "current_stage": {
                        "id": next_stage.id,
                        "name": next_stage.name,
                        "order": next_stage.order,
                    },
                    "finished": finished,
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

        # -----------------------------------------------------
        # ONLY ADMIN / COUNSELOR / SUPERUSER
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # VALIDATE STAGE ORDER
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # LOCK PROCESS
        # -----------------------------------------------------

        with transaction.atomic():

            try:
                process = (
                    StudentProcess.objects
                    .select_for_update()
                    .select_related(
                        "student",
                        "student__user",
                        "current_stage",
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

            # -------------------------------------------------
            # FIND TARGET STAGE
            # -------------------------------------------------

            try:
                target_stage = ProcessStage.objects.get(
                    order=stage_order
                )

            except ProcessStage.DoesNotExist:
                return Response(
                    {
                        "detail": (
                            f"Process Stage {stage_order} "
                            f"does not exist."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # -------------------------------------------------
            # CURRENT STAGE
            # -------------------------------------------------

            previous_stage = process.current_stage

            # Already on requested stage.
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

            # -------------------------------------------------
            # MARK PREVIOUS STAGE COMPLETED
            # -------------------------------------------------

            if previous_stage is not None:

                previous_history, _ = (
                    ProcessStageHistory.objects.get_or_create(
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

                previous_history.completed_at = (
                    timezone.now()
                )

                previous_history.updated_by = user

                previous_history.save(
                    update_fields=[
                        "status",
                        "completed_at",
                        "updated_by",
                    ]
                )

            # -------------------------------------------------
            # MOVE TO TARGET STAGE
            # -------------------------------------------------

            process.current_stage = target_stage

            process.save(
                update_fields=[
                    "current_stage",
                    "updated_at",
                ]
            )

            # -------------------------------------------------
            # CREATE / UPDATE TARGET HISTORY
            # -------------------------------------------------

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

            # -------------------------------------------------
            # STUDENT USER
            # -------------------------------------------------

            student_user = process.student.user

            # -------------------------------------------------
            # NOTIFICATION
            # -------------------------------------------------

            create_notification(
                user=student_user,
                title="Application Step Updated",
                message=(
                    f"Your application has been moved "
                    f"to Step {target_stage.order}: "
                    f"{target_stage.name}."
                ),
                notification_type=(
                    Notification.Type.INFO
                ),
            )

            # -------------------------------------------------
            # RESPONSE
            # -------------------------------------------------

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