from django.utils import timezone
from rest_framework import viewsets
from .models import DocumentType, Document
from .serializers import DocumentTypeSerializer, DocumentSerializer


class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related("student", "document_type").all()
    serializer_class = DocumentSerializer
    filterset_fields = ["student", "document_type", "status"]

    def perform_update(self, serializer):
        if serializer.validated_data.get("status") in ("approved", "rejected"):
            serializer.save(reviewed_by=self.request.user, reviewed_at=timezone.now())
        else:
            serializer.save()
