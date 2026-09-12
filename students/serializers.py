from rest_framework import serializers

from .models import (
    StudentProfile,
    StudentApplication,
    Education,
)

from rest_framework import serializers

from .models import (
    StudentProfile,
    StudentApplication,
    Education,
)


class EducationSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(
        source="country.name",
        read_only=True,
    )

    class Meta:
        model = Education
        fields = [
            "id",
            "degree_level",
            "institution_name",
            "gpa",
            "gpa_scale",
            "grade",
            "passout_year",
            "country",
            "country_name",
            "is_completed",
        ]

class EducationSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(
        source="country.name",
        read_only=True,
    )

    class Meta:
        model = Education
        fields = [
            "id",
            "degree_level",
            "institution_name",
            "field_of_study",
            "country",
            "country_name",
            "start_date",
            "end_date",
            "grade",
            "gpa",
            "gpa_scale",
            "passout_year",
            "is_completed",
        ]

class StudentDocumentSerializer(serializers.Serializer):
    name = serializers.CharField()
    field = serializers.CharField()
    url = serializers.CharField()


class UbtStudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    phone_number = serializers.CharField(
        source="user.phone_number",
        allow_blank=True,
        required=False,
    )

    email = serializers.EmailField(
        source="user.email"
    )

    documents = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "full_name",
            "phone_number",
            "email",
            "documents",
        ]

    def get_full_name(self, obj):
        return (
            f"{obj.user.first_name} "
            f"{obj.user.last_name}"
        ).strip()

    def get_documents(self, obj):
        try:
            application = obj.application
        except StudentApplication.DoesNotExist:
            return []

        document_fields = [
            ("Photo", "step1_photo"),
            ("Transcript", "transcript_file"),
            ("Confirmation File", "confirmation_file"),
            ("Offer Letter", "offer_file"),
            ("LOC", "loc_file"),
            ("Visa Approval Letter", "visa_approval_letter_file"),
            ("Flight Ticket", "ticket_file"),
        ]

        documents = []

        for name, field_name in document_fields:
            file_field = getattr(
                application,
                field_name,
                None,
            )

            if not file_field:
                continue

            try:
                url = file_field.url
            except Exception:
                continue

            if not url:
                continue

            documents.append(
                {
                    "name": name,
                    "field": field_name,
                    "url": url,
                }
            )

        return documents


class UbtStudentBasicInfoUpdateSerializer(
    serializers.Serializer
):
    full_name = serializers.CharField(
        required=False,
        allow_blank=False,
    )

    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    email = serializers.EmailField(
        required=False,
    )

    def validate_email(self, value):
        value = value.strip().lower()

        if (
            self.instance.user.email.lower() != value
            and self.instance.user.__class__.objects
            .filter(email__iexact=value)
            .exclude(pk=self.instance.user.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "This email address is already in use."
            )

        return value

    def update(self, instance, validated_data):
        user = instance.user

        if "full_name" in validated_data:
            full_name = validated_data[
                "full_name"
            ].strip()

            parts = full_name.split()

            user.first_name = (
                parts[0]
                if parts
                else ""
            )

            user.last_name = (
                " ".join(parts[1:])
                if len(parts) > 1
                else ""
            )

        if "phone_number" in validated_data:
            user.phone_number = (
                validated_data[
                    "phone_number"
                ].strip()
            )

        if "email" in validated_data:
            user.email = (
                validated_data[
                    "email"
                ].strip().lower()
            )

        user.save()

        return instance