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
    stage_history = ProcessStageHistorySerializer(
        many=True,
        read_only=True,
    )

    current_step = serializers.SerializerMethodField()
    completed_steps = serializers.SerializerMethodField()
    process_finished = serializers.SerializerMethodField()

    class Meta:
        model = StudentProcess
        fields = [
            "id",
            "student",
            "current_stage",
            "started_at",
            "updated_at",
            "stage_history",
            "current_step",
            "completed_steps",
            "process_finished",
        ]
        read_only_fields = [
            "started_at",
            "updated_at",
            "current_step",
            "completed_steps",
            "process_finished",
        ]

    def get_current_step(self, obj):
        if obj.current_stage is None:
            return 1

        return obj.current_stage.order

    def get_completed_steps(self, obj):
        return list(
            obj.stage_history
            .filter(
                status=ProcessStageHistory.Status.COMPLETED
            )
            .values_list(
                "stage__order",
                flat=True,
            )
            .order_by("stage__order")
        )

    def get_process_finished(self, obj):
        if obj.current_stage is None:
            return False

        return obj.stage_history.filter(
            stage=obj.current_stage,
            status=ProcessStageHistory.Status.COMPLETED,
        ).exists()