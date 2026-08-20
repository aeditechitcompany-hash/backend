from rest_framework import viewsets
from .models import ProcessStage, StudentProcess, ProcessStageHistory
from .serializers import ProcessStageSerializer, StudentProcessSerializer, ProcessStageHistorySerializer


class ProcessStageViewSet(viewsets.ModelViewSet):
    queryset = ProcessStage.objects.all()
    serializer_class = ProcessStageSerializer


class StudentProcessViewSet(viewsets.ModelViewSet):
    queryset = StudentProcess.objects.select_related("student", "current_stage").all()
    serializer_class = StudentProcessSerializer
    filterset_fields = ["student", "current_stage"]


class ProcessStageHistoryViewSet(viewsets.ModelViewSet):
    queryset = ProcessStageHistory.objects.all()
    serializer_class = ProcessStageHistorySerializer
    filterset_fields = ["student_process", "stage", "status"]
