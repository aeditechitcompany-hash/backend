from rest_framework import viewsets
from .models import VisaApplication, VisaDocument
from .serializers import VisaApplicationSerializer, VisaDocumentSerializer


class VisaApplicationViewSet(viewsets.ModelViewSet):
    queryset = VisaApplication.objects.select_related("student", "country", "application").all()
    serializer_class = VisaApplicationSerializer
    filterset_fields = ["student", "country", "status"]


class VisaDocumentViewSet(viewsets.ModelViewSet):
    queryset = VisaDocument.objects.all()
    serializer_class = VisaDocumentSerializer
    filterset_fields = ["visa_application", "document"]
