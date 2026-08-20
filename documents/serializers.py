from rest_framework import serializers
from .models import DocumentType, Document


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["uploaded_at", "reviewed_by", "reviewed_at"]
