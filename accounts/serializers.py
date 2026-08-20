from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers

from .models import User, OTP, LoginHistory, Role, FeaturePermission, UserRole


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "phone_number", "role", "province", "district", "street_address", "first_name", "last_name",
            "profile_picture", "is_email_verified", "is_phone_verified", "is_active_student",
            "created_at",
        ]
        read_only_fields = ["id", "is_email_verified", "is_phone_verified", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number", "password", "first_name", "last_name", "role", "street_address", "province", "district"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        attrs["user"] = user
        return attrs


class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=OTP.Purpose.choices)


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=OTP.Purpose.choices)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        otp = OTP.objects.filter(
            user=user, code=attrs["code"], purpose=attrs["purpose"], is_used=False
        ).order_by("-created_at").first()
        if not otp or not otp.is_valid():
            raise serializers.ValidationError("Invalid or expired OTP")
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