
from rest_framework import serializers

from .models import Book, StudentBookAccess


class BookSerializer(serializers.ModelSerializer):
    access_status = serializers.SerializerMethodField()
    has_access = serializers.SerializerMethodField()

    pdf = serializers.FileField(
        write_only=True,
        required=False,
    )

    class Meta:
        model = Book
        fields = (
            "id",
            "category",
            "title",
            "author",
            "description",
            "price",
            "cover",
            "pdf",
            "uploaded_by",
            "featured",
            "is_active",
            "total_views",
            "total_downloads",
            "created_at",
            "updated_at",
            "access_status",
            "has_access",
        )
        read_only_fields = (
            "id",
            "total_views",
            "total_downloads",
            "created_at",
            "updated_at",
            "access_status",
            "has_access",
        )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            user = request.user
            is_staff_user = (
                user.is_superuser
                or getattr(user, "role", None) in ("admin", "counselor")
            )

            if not is_staff_user:
                fields.pop("pdf", None)

        return fields

    def _get_student_access(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return None

        if getattr(request.user, "role", None) != "student":
            return None

        # Use prefetched access records when available.
        prefetched = getattr(obj, "_request_student_access", None)
        if prefetched is not None:
            return prefetched[0] if prefetched else None

        try:
            return StudentBookAccess.objects.get(
                student__user=request.user,
                book=obj,
            )
        except StudentBookAccess.DoesNotExist:
            return None

    def get_access_status(self, obj):
        access = self._get_student_access(obj)

        if access is None:
            return "not_purchased"

        if access.status == StudentBookAccess.Status.APPROVED:
            return "approved" if access.is_valid else "expired"

        return access.status

    def get_has_access(self, obj):
        access = self._get_student_access(obj)
        return bool(access and access.is_valid)
