from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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