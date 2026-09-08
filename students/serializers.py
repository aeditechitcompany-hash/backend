from rest_framework import serializers
from .models import StudentProcess
from .models import StudentProfile, Education, Preferences


class EducationSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(),
        required=False,
    )

    country_name = serializers.CharField(
        source="country.name",
        read_only=True,
    )

    class Meta:
        model = Education
        fields = "__all__"
        extra_fields = ["country_name"]


class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = "__all__"


class StudentProfileSerializer(serializers.ModelSerializer):
    education_history = EducationSerializer(
        many=True,
        read_only=True,
    )

    preferences = PreferencesSerializer(
        read_only=True,
    )

    # --------------------------------------------------------
    # PROCESS INFORMATION
    # --------------------------------------------------------

    process_id = serializers.SerializerMethodField()

    current_process_step = serializers.SerializerMethodField()

    current_process_stage = serializers.SerializerMethodField()

    process_finished = serializers.SerializerMethodField()

    def get_process_id(self, obj):
        try:
            return obj.process.id
        except Exception:
            return None

    def get_current_process_step(self, obj):
        try:
            return obj.process.current_stage.order
        except Exception:
            return 1

    def get_current_process_stage(self, obj):
        try:
            stage = obj.process.current_stage

            if stage is None:
                return None

            return {
                "id": stage.id,
                "name": stage.name,
                "order": stage.order,
                "description": stage.description,
            }

        except Exception:
            return None

    def get_process_finished(self, obj):
        try:
            process = obj.process

            if process.current_stage is None:
                return True

            from .models import StudentProcess

            # If there is no stage after the current stage,
            # the current stage is the final stage.
            from process.models import ProcessStage

            has_next_stage = ProcessStage.objects.filter(
                order__gt=process.current_stage.order
            ).exists()

            return not has_next_stage

        except Exception:
            return False

    class Meta:
        model = StudentProfile

        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "profile_completion_percentage",
        ]