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
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        read_only=True,
    )
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    phone_number = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )
    role = serializers.CharField(
        source="user.role",
        read_only=True,
    )
    user_created_at = serializers.DateTimeField(
        source="user.created_at",
        read_only=True,
    )

    education_history = serializers.SerializerMethodField()
    application = serializers.SerializerMethodField()

    process_id = serializers.SerializerMethodField()
    current_process_step = serializers.SerializerMethodField()
    completed_process_steps = serializers.SerializerMethodField()
    current_process_stage = serializers.SerializerMethodField()
    process_finished = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            "id",

            # User
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "user_created_at",

            # Profile
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

            # Process
            "process_id",
            "current_process_step",
            "completed_process_steps",
            "current_process_stage",
            "process_finished",

            # Related data
            "education_history",
            "application",
        ]

        read_only_fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "user_created_at",
            "created_at",
            "updated_at",
            "process_id",
            "current_process_step",
            "completed_process_steps",
            "current_process_stage",
            "process_finished",
            "education_history",
            "application",
        ]

    def get_education_history(self, obj):
        education = obj.education_history.all()

        return EducationSerializer(
            education,
            many=True,
            context=self.context,
        ).data

    def get_application(self, obj):
        try:
            application = obj.application
        except StudentApplication.DoesNotExist:
            return None

        return StudentApplicationSerializer(
            application,
            context=self.context,
        ).data

    def get_process_id(self, obj):
        try:
            return str(obj.process.id)
        except Exception:
            return None

    def get_current_process_step(self, obj):
        try:
            process = obj.process

            if process.current_stage:
                return process.current_stage.order

            return obj.current_step or 1
        except Exception:
            return obj.current_step or 1

    def get_completed_process_steps(self, obj):
        try:
            process = obj.process

            return list(
                process.stage_history
                .filter(
                    status=ProcessStageHistory.Status.COMPLETED
                )
                .values_list(
                    "stage__order",
                    flat=True,
                )
            )
        except Exception:
            return []

    def get_current_process_stage(self, obj):
        try:
            stage = obj.process.current_stage

            if not stage:
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

            if not process.current_stage:
                return False

            history = process.stage_history.filter(
                stage=process.current_stage
            ).first()

            return (
                history is not None
                and history.status
                == ProcessStageHistory.Status.COMPLETED
            )
        except Exception:
            return False