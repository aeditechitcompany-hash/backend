from django.utils import timezone
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, OTP, LoginHistory, Role, FeaturePermission, UserRole
from .permissions import IsAdmin, IsCounselor
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, OTPRequestSerializer,
    OTPVerifySerializer, LoginHistorySerializer, RoleSerializer,
    FeaturePermissionSerializer, UserRoleSerializer,
)
import logging

logger = logging.getLogger(__name__)



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class BaseLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    allowed_roles = None

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]

            if self.allowed_roles is not None and not (
                user.is_superuser or user.role in self.allowed_roles
            ):
                return Response(
                    {"detail": "This account does not have access to this login portal."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if not user.is_active:
                return Response(
                    {"detail": "This account is disabled."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            refresh = RefreshToken.for_user(user)

            refresh["role"] = user.role
            refresh["is_staff"] = user.is_staff
            refresh["email"] = user.email
            refresh.access_token["role"] = user.role
            refresh.access_token["is_staff"] = user.is_staff
            refresh.access_token["email"] = user.email

            LoginHistory.objects.create(
                user=user,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
            )

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            })

        except Exception:
            logger.exception("LOGIN ERROR")
            raise


class LoginView(BaseLoginView):
    """Generic login — any role may use it. Kept for a single unified app."""
    allowed_roles = None


class StudentLoginView(BaseLoginView):
    allowed_roles = [User.Role.STUDENT]


class CounselorLoginView(BaseLoginView):
    allowed_roles = [User.Role.COUNSELOR]


class AdminLoginView(BaseLoginView):
    allowed_roles = [User.Role.ADMIN]


class RequestOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data["email"])
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        otp = OTP.objects.create(user=user, purpose=serializer.validated_data["purpose"])
        # In production: send OTP via email/SMS instead of returning it
        return Response({"detail": "OTP generated", "code": otp.code}, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data["otp"]
        user = serializer.validated_data["user"]
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        if otp.purpose == OTP.Purpose.EMAIL_VERIFICATION:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])
        elif otp.purpose == OTP.Purpose.PHONE_VERIFICATION:
            user.is_phone_verified = True
            user.save(update_fields=["is_phone_verified"])
        return Response({"detail": "OTP verified"})


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    """
    Admins/Counselors: see every user.
    Students: only ever see/edit their own record (list is filtered to themselves).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ["role", "is_email_verified", "is_active_student", "province", "district", ]
    search_fields = ["email", "username", "first_name", "last_name","street_address"]
    pagination_class = None  # frontend expects a plain JSON array, not {count, results}

    def get_permissions(self):
        if self.action in ("create", "destroy"):
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.role in (User.Role.ADMIN, User.Role.COUNSELOR):
            return qs
        return qs.filter(id=user.id)  # students only ever see themselves


class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoginHistory.objects.all()
    serializer_class = LoginHistorySerializer
    filterset_fields = ["user", "is_active"]
    permission_classes = [IsCounselor]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]


class FeaturePermissionViewSet(viewsets.ModelViewSet):
    queryset = FeaturePermission.objects.all()
    serializer_class = FeaturePermissionSerializer
    filterset_fields = ["role", "module", "action"]
    permission_classes = [IsAdmin]


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    filterset_fields = ["user", "role"]
    permission_classes = [IsAdmin]