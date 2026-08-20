from rest_framework import serializers
from .models import ProcessStage, StudentProcess, ProcessStageHistory


class ProcessStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStage
        fields = "__all__"


class ProcessStageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStageHistory
        fields = "__all__"
        read_only_fields = ["updated_by"]


class StudentProcessSerializer(serializers.ModelSerializer):
    stage_history = ProcessStageHistorySerializer(many=True, read_only=True)

    class Meta:
        model = StudentProcess
        fields = "__all__"
        read_only_fields = ["started_at", "updated_at"]
