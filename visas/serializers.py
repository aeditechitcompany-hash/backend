from rest_framework import serializers
from .models import VisaApplication, VisaDocument


class VisaDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaDocument
        fields = "__all__"


class VisaApplicationSerializer(serializers.ModelSerializer):
    visa_documents = VisaDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = VisaApplication
        fields = "__all__"
