from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from notifications.services import create_notification
from notifications.models import Notification

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


class StudentProcessViewSet(viewsets.ModelViewSet):
    queryset = StudentProcess.objects.select_related(
        "student",
        "student__user",
        "current_stage",
    ).all()

    serializer_class = StudentProcessSerializer

    filterset_fields = [
        "student",
        "current_stage",
    ]

    @action(
        detail=True,
        methods=["post"],
        url_path="complete-stage",
        permission_classes=[IsAuthenticated],
    )
    def complete_stage(self, request, pk=None):
        user = request.user

        # Only admin/counselor/superuser can process a stage.
        if not (
            user.is_superuser
            or getattr(user, "role", None) in ["admin", "counselor"]
        ):
            return Response(
                {
                    "detail": (
                        "Only admins and counselors can "
                        "complete process stages."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            process = (
                StudentProcess.objects
                .select_for_update()
                .select_related(
                    "current_stage",
                    "student__user",
                )
                .get(pk=pk)
            )

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

            previous_stage = process.current_stage

            result = process.complete_current_stage(
                updated_by=user,
            )

            process.refresh_from_db()

            serializer = self.get_serializer(process)

        if result["finished"]:
            create_notification(
                user=student_user,
                title="Application Process Completed",
                message=(
                    "Congratulations! You have completed all "
                    "steps of your application process."
                ),
                notification_type=Notification.Type.SUCCESS,
            )
        else:
            create_notification(
                user=student_user,
                title=f"Step {previous_stage.order} Completed",
                message=(
                    f"Your application has completed "
                    f"Step {previous_stage.order}: "
                    f"{previous_stage.name}. "
                    f"You have now moved to Step "
                    f"{process.current_stage.order}: "
                    f"{process.current_stage.name}."
                ),
                notification_type=Notification.Type.INFO,
            )
            message = (
                f"Stage '{previous_stage.name}' completed. "
                "All process stages are now completed."
            )

        if result["finished"]:
            message = (
                f"Stage '{previous_stage.name}' completed. "
                "All process stages are now completed."
            )
        else:
            message = (
                f"Stage '{previous_stage.name}' completed. "
                f"Student moved to "
                f"'{process.current_stage.name}'."
            )

        return Response(
            {
                "detail": message,
                "completed": True,
                "finished": result["finished"],
                "previous_stage": {
                    "id": previous_stage.id,
                    "name": previous_stage.name,
                    "order": previous_stage.order,
                },
                "current_stage": (
                    None
                    if result["finished"]
                    else {
                        "id": process.current_stage.id,
                        "name": process.current_stage.name,
                        "order": process.current_stage.order,
                    }
                ),
                "student_process": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="set-stage",
        permission_classes=[IsAuthenticated],
    )
    def set_stage(self, request, pk=None):
        user = request.user

        # Only admin/counselor/superuser can manually change a stage.
        if not (
            user.is_superuser
            or getattr(user, "role", None) in ["admin", "counselor"]
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
                    "detail": "stage_order must be an integer."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            process = (
                StudentProcess.objects
                .select_for_update()
                .select_related(
                    "current_stage",
                    "student__user",
                )
                .get(pk=pk)
            )

            stage = (
                ProcessStage.objects
                .filter(order=stage_order)
                .first()
            )

            if stage is None:
                return Response(
                    {
                        "detail": (
                            f"Process stage with order "
                            f"{stage_order} does not exist."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            previous_stage = process.current_stage

            process.current_stage = stage
            process.save(
                update_fields=[
                    "current_stage",
                    "updated_at",
                ]
            )
            create_notification(
                user=process.student.user,
                title="Application Step Updated",
                message=(
                    f"Your application has been moved to "
                    f"Step {stage.order}: {stage.name}."
                ),
                notification_type=Notification.Type.INFO,
            )

            # Mark the selected stage as the active/in-progress stage.
            ProcessStageHistory.objects.update_or_create(
                student_process=process,
                stage=stage,
                defaults={
                    "status": ProcessStageHistory.Status.IN_PROGRESS,
                    "updated_by": user,
                    "completed_at": None,
                },
            )

            process.refresh_from_db()

            serializer = self.get_serializer(process)

        return Response(
            {
                "detail": (
                    f"Student moved to "
                    f"'{stage.name}' (Step {stage.order})."
                ),
                "previous_stage": (
                    None
                    if previous_stage is None
                    else {
                        "id": previous_stage.id,
                        "name": previous_stage.name,
                        "order": previous_stage.order,
                    }
                ),
                "current_stage": {
                    "id": stage.id,
                    "name": stage.name,
                    "order": stage.order,
                },
                "student_process": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProcessStageHistoryViewSet(viewsets.ModelViewSet):
    queryset = ProcessStageHistory.objects.select_related(
        "student_process",
        "stage",
        "updated_by",
    ).all()

    serializer_class = ProcessStageHistorySerializer

    filterset_fields = [
        "student_process",
        "stage",
        "status",
    ]