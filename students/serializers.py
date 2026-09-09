from rest_framework import serializers

from .models import (
    StudentProfile,
    Education,
    Preferences,
    StudentApplication,
)
from process.models import ProcessStageHistory


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

class StudentApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentApplication
        fields = "__all__"

        read_only_fields = [
            "id",
            "student",
            "created_at",
            "updated_at",
        ]

class StudentProfileSerializer(serializers.ModelSerializer):
    education_history = EducationSerializer(
        many=True,
        read_only=True,
    )

    application = serializers.SerializerMethodField()

    preferences = PreferencesSerializer(
        read_only=True,
    )

    application = StudentApplicationSerializer(
        read_only=True,
    )

    # --------------------------------------------------------
    # PROCESS INFORMATION
    # --------------------------------------------------------

    process_id = serializers.SerializerMethodField()

    current_process_step = serializers.SerializerMethodField()

    completed_process_steps = serializers.SerializerMethodField()

    current_process_stage = serializers.SerializerMethodField()

    process_finished = serializers.SerializerMethodField()

    # --------------------------------------------------------
    # PROCESS ID
    # --------------------------------------------------------

    def get_process_id(self, obj):
        try:
            return str(obj.process.id)
        except Exception:
            return None

    # --------------------------------------------------------
    # CURRENT PROCESS STEP
    # --------------------------------------------------------

    def get_current_process_step(self, obj):
        try:
            process = obj.process

            if process.current_stage is None:
                return 1

            return process.current_stage.order

        except Exception:
            return 1

    # --------------------------------------------------------
    # COMPLETED PROCESS STEPS
    # --------------------------------------------------------

    def get_completed_process_steps(self, obj):
        try:
            process = obj.process

            return list(
                process.stage_history
                .filter(
                    status=ProcessStageHistory.Status.COMPLETED,
                )
                .values_list(
                    "stage__order",
                    flat=True,
                )
                .order_by(
                    "stage__order",
                )
            )

        except Exception:
            return []

    # --------------------------------------------------------
    # CURRENT PROCESS STAGE
    # --------------------------------------------------------

    def get_current_process_stage(self, obj):
        try:
            process = obj.process
            stage = process.current_stage

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

    # --------------------------------------------------------
    # PROCESS FINISHED
    # --------------------------------------------------------

    def get_process_finished(self, obj):
        try:
            process = obj.process

            if process.current_stage is None:
                return False

            return process.stage_history.filter(
                stage=process.current_stage,
                status=ProcessStageHistory.Status.COMPLETED,
            ).exists()

        except Exception:
            return False
    def get_application(self, obj):
        try:
            return StudentApplicationSerializer(
                obj.application
            ).data
        except StudentApplication.DoesNotExist:
            return None
    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    class Meta:
        model = StudentProfile

        fields = [
            "id",
            "user",
            "date_of_birth",
            "gender",
            "nationality",
            "passport_number",
            "address",
            "city",
            "country",
            "emergency_contact_name",
            "emergency_contact_phone",
            "bio",
            "profile_completion_percentage",
            "assigned_counselor",
            "current_step",
            "mcq_access",
            "book_access",
            "created_at",
            "updated_at",

            # Related data
            "education_history",
            "preferences",
            "application",

            # Process data
            "process_id",
            "current_process_step",
            "completed_process_steps",
            "current_process_stage",
            "process_finished",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "profile_completion_percentage",
        ]