from rest_framework import viewsets
from .models import Interview
from .serializers import InterviewSerializer


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.select_related("application").all()
    serializer_class = InterviewSerializer
    filterset_fields = ["application", "status", "mode", "result"]
