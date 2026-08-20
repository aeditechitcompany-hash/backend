from rest_framework import serializers

from .models import StudentProfile, Education, Preferences


class EducationSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(),
        required=False,
    )

    country_name = serializers.CharField(
        source="country.name",
        read_only=True
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

    class Meta:
        model = StudentProfile
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "profile_completion_percentage",
        ]