
import logging
from io import BytesIO

from django.db.models import F, Prefetch
from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsCounselor
from students.models import StudentProfile

from .models import Book, StudentBookAccess
from .serializers import BookSerializer


logger = logging.getLogger(__name__)


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [IsCounselor()]

        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        queryset = Book.objects.select_related(
            "category",
            "uploaded_by",
        )

        is_staff_user = (
            user.is_superuser
            or getattr(user, "role", None) in ("admin", "counselor")
        )

        if is_staff_user:
            return queryset.order_by("-created_at")

        if getattr(user, "role", None) != "student":
            raise PermissionDenied(
                "You are not authorized to access the Books module."
            )

        try:
            profile = user.student_profile
        except StudentProfile.DoesNotExist:
            raise PermissionDenied("Student profile not found.")

        queryset = queryset.filter(is_active=True)

        return queryset.prefetch_related(
            Prefetch(
                "student_access_records",
                queryset=StudentBookAccess.objects.filter(
                    student=profile
                ),
                to_attr="_request_student_access",
            )
        ).order_by("-created_at")

    @action(
        detail=True,
        methods=["get"],
        url_path="open",
        permission_classes=[IsAuthenticated],
    )
    def open_book(self, request, pk=None):
        book = self.get_object()
        user = request.user

        is_staff_user = (
            user.is_superuser
            or getattr(user, "role", None) in ("admin", "counselor")
        )

        if not is_staff_user:
            if getattr(user, "role", None) != "student":
                raise PermissionDenied(
                    "You are not authorized to open this book."
                )

            try:
                profile = user.student_profile
            except StudentProfile.DoesNotExist:
                raise PermissionDenied("Student profile not found.")

            access = StudentBookAccess.objects.filter(
                student=profile,
                book=book,
            ).first()

            if not access or not access.is_valid:
                return Response(
                    {
                        "detail": "You do not have active access to this book.",
                        "access_status": (
                            access.status if access else "not_purchased"
                        ),
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        if not book.pdf:
            return Response(
                {"detail": "PDF file is not available."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            pdf_data = book.pdf.storage.download(book.pdf.name)

            if not pdf_data:
                return Response(
                    {"detail": "PDF file is empty."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            Book.objects.filter(pk=book.pk).update(
                total_views=F("total_views") + 1
            )

            response = FileResponse(
                BytesIO(pdf_data),
                as_attachment=False,
                filename=f"{book.title}.pdf",
                content_type="application/pdf",
            )

            response["Cache-Control"] = "private, no-store"
            response["Pragma"] = "no-cache"
            response["X-Content-Type-Options"] = "nosniff"

            return response

        except Exception:
            logger.exception(
                "Unable to retrieve PDF for book %s",
                book.pk,
            )

            return Response(
                {"detail": "Unable to open this book right now."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
