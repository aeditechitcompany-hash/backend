from rest_framework import serializers
from .models import Application, ApplicationStatusHistory


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatusHistory
        fields = "__all__"
        read_only_fields = ["changed_by", "changed_at"]


class ApplicationSerializer(serializers.ModelSerializer):
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
