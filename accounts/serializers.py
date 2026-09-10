import re
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers

from students.models import StudentProfile
from process.models import ProcessStageHistory

from .models import (
    User,
    OTP,
    LoginHistory,
    PasswordResetToken,
    Role,
    FeaturePermission,
    UserRole,
)


class UserSerializer(serializers.ModelSerializer):
    # ------------------------------------------------------------
    # STUDENT PROCESS INFORMATION
    # ------------------------------------------------------------

    process_id = serializers.SerializerMethodField()
    current_process_step = serializers.SerializerMethodField()
    completed_process_steps = serializers.SerializerMethodField()
    current_process_stage = serializers.SerializerMethodField()
    process_finished = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "role",
            "province",
            "district",
            "street_address",
            "first_name",
            "last_name",
            "profile_picture",
            "is_email_verified",
            "is_phone_verified",
            "is_active_student",
            "created_at",

            # ----------------------------------------------------
            # PROCESS FIELDS
            # ----------------------------------------------------
            "process_id",
            "current_process_step",
            "completed_process_steps",
            "current_process_stage",
            "process_finished",
        ]

        read_only_fields = [
            "id",
            "is_email_verified",
            "is_phone_verified",
            "created_at",

            # Process fields are calculated from StudentProcess
            "process_id",
            "current_process_step",
            "completed_process_steps",
            "current_process_stage",
            "process_finished",
        ]

    # ------------------------------------------------------------
    # GET STUDENT PROFILE
    # ------------------------------------------------------------

    def _get_student_profile(self, obj):
        """
        Return the StudentProfile belonging to this user.

        UBT users may also have a StudentProfile, so we don't
        assume that only role='student' has one.
        """
        try:
            return obj.student_profile
        except StudentProfile.DoesNotExist:
            return None
        except Exception:
            return None

    # ------------------------------------------------------------
    # PROCESS ID
    # ------------------------------------------------------------

    def get_process_id(self, obj):
        profile = self._get_student_profile(obj)

        if profile is None:
            return None

        try:
            return str(profile.process.id)
        except Exception:
            return None

    # ------------------------------------------------------------
    # CURRENT PROCESS STEP
    # ------------------------------------------------------------

    def get_current_process_step(self, obj):
        profile = self._get_student_profile(obj)

        if profile is None:
            return 1

        try:
            process = profile.process

            if process.current_stage is None:
                return 1

            return process.current_stage.order

        except Exception:
            return 1

    # ------------------------------------------------------------
    # COMPLETED PROCESS STEPS
    # ------------------------------------------------------------

    def get_completed_process_steps(self, obj):
        profile = self._get_student_profile(obj)

        if profile is None:
            return []

        try:
            process = profile.process

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

    # ------------------------------------------------------------
    # CURRENT PROCESS STAGE
    # ------------------------------------------------------------

    def get_current_process_stage(self, obj):
        profile = self._get_student_profile(obj)

        if profile is None:
            return None

        try:
            process = profile.process
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

    # ------------------------------------------------------------
    # PROCESS FINISHED
    # ------------------------------------------------------------

    def get_process_finished(self, obj):
        profile = self._get_student_profile(obj)

        if profile is None:
            return False

        try:
            process = profile.process

            if process.current_stage is None:
                return False

            return process.stage_history.filter(
                stage=process.current_stage,
                status=ProcessStageHistory.Status.COMPLETED,
            ).exists()

        except Exception:
            return False


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "password",
            "first_name",
            "last_name",
            "role",
            "street_address",
            "province",
            "district",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)

        user.set_password(password)

        user.save()

        # ------------------------------------------------------------
        # CREATE MINIMAL STUDENT PROFILE FOR UBT
        # ------------------------------------------------------------

        if user.role == User.Role.UBT:
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "mcq_access": False,
                    "book_access": False,
                },
            )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        user = authenticate(
            email=attrs["email"],
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials"
            )

        attrs["user"] = user

        return attrs


class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=OTP.Purpose.choices,
    )


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(
        max_length=6,
    )
    purpose = serializers.ChoiceField(
        choices=OTP.Purpose.choices,
    )

    def validate(self, attrs):
        try:
            user = User.objects.get(
                email=attrs["email"]
            )

        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User not found"
            )

        otp = (
            OTP.objects
            .filter(
                user=user,
                code=attrs["code"],
                purpose=attrs["purpose"],
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp or not otp.is_valid():
            raise serializers.ValidationError(
                "Invalid or expired OTP"
            )

        attrs["user"] = user
        attrs["otp"] = otp

        return attrs


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class FeaturePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturePermission
        fields = "__all__"


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = "__all__"

class PasswordForgotSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordVerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    code = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        code = attrs["code"].strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid email or OTP."
            )

        otp = (
            OTP.objects
            .filter(
                user=user,
                purpose=OTP.Purpose.PASSWORD_RESET,
                code=code,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp or not otp.is_valid():
            raise serializers.ValidationError(
                "Invalid or expired OTP."
            )

        attrs["user"] = user
        attrs["otp"] = otp

        return attrs


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate(self, attrs):
        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirm_password": "Passwords do not match."
                }
            )

        if not re.search(r"[A-Z]", new_password):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", new_password):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"[0-9]", new_password):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not re.search(
            r'[!@#$&*~%^()_\-+=\[\]{};:,.<>?/\\|`]',
            new_password,
        ):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        try:
            reset_token = PasswordResetToken.objects.get(
                token=attrs["token"],
                is_used=False,
            )
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid or expired reset token."
            )

        if timezone.now() > reset_token.expires_at:
            raise serializers.ValidationError(
                "Invalid or expired reset token."
            )

        attrs["reset_token"] = reset_token

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate(self, attrs):
        user = self.context["request"].user

        current_password = attrs["current_password"]
        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        if not user.check_password(current_password):
            raise serializers.ValidationError(
                {
                    "current_password":
                        "Current password is incorrect."
                }
            )

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirm_password":
                        "Passwords do not match."
                }
            )

        if current_password == new_password:
            raise serializers.ValidationError(
                {
                    "new_password":
                        "New password must be different from current password."
                }
            )

        if not re.search(r"[A-Z]", new_password):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", new_password):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"[0-9]", new_password):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not re.search(
            r'[!@#$&*~%^()_\-+=\[\]{};:,.<>?/\\|`]',
            new_password,
        ):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return attrs