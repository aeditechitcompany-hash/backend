from rest_framework import viewsets
from .models import Application, ApplicationStatusHistory
from .serializers import ApplicationSerializer, ApplicationStatusHistorySerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related("student", "university", "course").all()
    serializer_class = ApplicationSerializer
    filterset_fields = ["student", "university", "course", "status", "handled_by"]
    search_fields = ["student__user__email", "university__name"]

    def perform_update(self, serializer):
        instance = serializer.save()
        if "status" in serializer.validated_data:
            ApplicationStatusHistory.objects.create(
                application=instance,
                status=instance.status,
                changed_by=self.request.user if self.request.user.is_authenticated else None,
            )


class ApplicationStatusHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApplicationStatusHistory.objects.all()
    serializer_class = ApplicationStatusHistorySerializer
    filterset_fields = ["application", "status"]
