from rest_framework import permissions

from .models import User
from students.models import StudentProfile


class IsAdmin(permissions.BasePermission):
    """Full access — only Role.ADMIN or Django superusers/staff."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (user.is_superuser or user.role == User.Role.ADMIN)
        )


class IsCounselor(permissions.BasePermission):
    """Staff-side access — counselors and admins."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated
            and (user.is_superuser or user.role in (User.Role.ADMIN, User.Role.COUNSELOR))
        )


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.Role.STUDENT)


class IsAdminOrCounselorOrReadOnlyOwner(permissions.BasePermission):
    """
    Admin/Counselor: full access to everything.
    Student: can only read/write their OWN related object.
    Object must expose `.user` or `.student.user` to compare against request.user.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or user.role in (User.Role.ADMIN, User.Role.COUNSELOR):
            return True
        owner = getattr(obj, "user", None) or getattr(getattr(obj, "student", None), "user", None)
        return owner == user



class HasMCQAccess(permissions.BasePermission):
    message = "You do not have permission to access the MCQ module."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or user.role in (
            User.Role.ADMIN,
            User.Role.COUNSELOR,
        ):
            return True

        try:
            student = StudentProfile.objects.get(user=user)
            return student.mcq_access
        except StudentProfile.DoesNotExist:
            return False