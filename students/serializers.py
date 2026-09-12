from rest_framework import serializers

from .models import (
    StudentProfile,
    StudentApplication,
    Education,
    Preferences,
)


# ============================================================
# STUDENT PROFILE
# ============================================================

class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    phone_number = serializers.CharField(
        source="user.phone_number",
        read_only=True,
        allow_blank=True,
    )

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
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
        ]

    def get_full_name(self, obj):
        return (
            f"{obj.user.first_name} "
            f"{obj.user.last_name}"
        ).strip()


# ============================================================
# EDUCATION
# ============================================================

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


# ============================================================
# PREFERENCES
# ============================================================

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = [
            "id",
            "student",
            "preferred_countries",
            "preferred_universities",
            "preferred_study_level",
            "preferred_courses",
            "preferred_intake",
            "budget_min",
            "budget_max",
            "notes",
        ]

        read_only_fields = [
            "id",
        ]


# ============================================================
# STUDENT APPLICATION
# ============================================================

class StudentApplicationSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = StudentApplication

        fields = [
            "id",
            "student",

            # STEP 1
            "step1_photo",
            "transcript_file",

            # STEP 4
            "interview_date",
            "interview_mode",
            "interview_result",
            "interview_notes",

            # STEP 5
            "application_ref_no",
            "submission_date",
            "confirmation_file",

            # STEP 6
            "offer_file",
            "offer_type",
            "offer_expiry_date",

            # STEP 7
            "loc_file",
            "loc_verified",

            # STEP 8
            "course_commencement_date",
            "scholarship_status",
            "final_selection_notes",
            "final_selection_confirmed",

            # STEP 9
            "visa_ref_no",
            "visa_status_update",
            "visa_approval_letter_file",

            # STEP 10
            "flight_number",
            "airline",
            "departure_airport",
            "arrival_airport",
            "departure_date_time",
            "ticket_file",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student",
            "created_at",
            "updated_at",
        ]


# ============================================================
# UBT DOCUMENT
# ============================================================

class StudentDocumentSerializer(
    serializers.Serializer
):
    name = serializers.CharField()
    field = serializers.CharField()
    url = serializers.CharField()


# ============================================================
# UBT STUDENT
# ============================================================

class UbtStudentSerializer(
    serializers.ModelSerializer
):
    full_name = serializers.SerializerMethodField()

    phone_number = serializers.CharField(
        source="user.phone_number",
        allow_blank=True,
        required=False,
    )

    email = serializers.EmailField(
        source="user.email",
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
            (
                "Visa Approval Letter",
                "visa_approval_letter_file",
            ),
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

            documents.append({
                "name": name,
                "field": field_name,
                "url": url,
            })

        return documents


# ============================================================
# UBT BASIC INFORMATION UPDATE
# ============================================================

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

        user_model = self.instance.user.__class__

        if (
            self.instance.user.email.lower() != value
            and user_model.objects
            .filter(email__iexact=value)
            .exclude(pk=self.instance.user.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "This email address is already in use."
            )

        return value

    def update(
        self,
        instance,
        validated_data,
    ):
        user = instance.user

        # -------------------------
        # FULL NAME
        # -------------------------

        if "full_name" in validated_data:

            full_name = (
                validated_data["full_name"]
                .strip()
            )

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

        # -------------------------
        # PHONE
        # -------------------------

        if "phone_number" in validated_data:
            user.phone_number = (
                validated_data[
                    "phone_number"
                ].strip()
            )

        # -------------------------
        # EMAIL
        # -------------------------

        if "email" in validated_data:
            user.email = (
                validated_data[
                    "email"
                ].strip()
                .lower()
            )

        user.save()

        return instance