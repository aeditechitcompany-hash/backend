from rest_framework import viewsets
from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filterset_fields = ["report_type", "generated_by"]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user if self.request.user.is_authenticated else None)
