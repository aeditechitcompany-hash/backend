from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, StudentLoginView, CounselorLoginView, AdminLoginView,
    RequestOTPView, VerifyOTPView, MeView,
    UserViewSet, LoginHistoryViewSet, RoleViewSet, FeaturePermissionViewSet, UserRoleViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"login-history", LoginHistoryViewSet, basename="login-history")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"permissions", FeaturePermissionViewSet, basename="permission")
router.register(r"user-roles", UserRoleViewSet, basename="user-role")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/login/student/", StudentLoginView.as_view(), name="login-student"),
    path("auth/login/counselor/", CounselorLoginView.as_view(), name="login-counselor"),
    path("auth/login/admin/", AdminLoginView.as_view(), name="login-admin"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/otp/request/", RequestOTPView.as_view(), name="otp-request"),
    path("auth/otp/verify/", VerifyOTPView.as_view(), name="otp-verify"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
