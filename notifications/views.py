from django.contrib.auth import get_user_model

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification, NotificationTemplate
from .serializers import (
    NotificationSerializer,
    NotificationTemplateSerializer,
    PublishNotificationSerializer,
)


User = get_user_model()


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user

        if (
            user.is_superuser
            or getattr(user, "role", None) in ["admin", "counselor"]
        ):
            return NotificationTemplate.objects.all()

        return NotificationTemplate.objects.none()


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ["notification_type", "is_read"]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response(
            NotificationSerializer(notification).data
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="publish",
    )
    def publish(self, request):
        """
        Admin/counselor publishes a notification
        to one or more students.
        """

        user = request.user

        # -----------------------------------------
        # Permission check
        # -----------------------------------------
        is_staff_role = (
            user.is_superuser
            or getattr(user, "role", None) in [
                "admin",
                "counselor",
            ]
        )

        if not is_staff_role:
            return Response(
                {
                    "detail": "You do not have permission to publish notifications."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # -----------------------------------------
        # Validate request
        # -----------------------------------------
        serializer = PublishNotificationSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user_ids = data.get("user_ids", [])
        send_to_all_students = data.get(
            "send_to_all_students",
            False,
        )

        title = data["title"]
        message = data["message"]
        notification_type = data["notification_type"]

        # -----------------------------------------
        # Find recipients
        # -----------------------------------------
        if send_to_all_students:
            recipients = User.objects.filter(
                role="student",
                is_active=True,
            )
        else:
            recipients = User.objects.filter(
                id__in=user_ids,
                role="student",
                is_active=True,
            )

        # -----------------------------------------
        # Create notifications
        # -----------------------------------------
        notifications = [
            Notification(
                user=student,
                title=title,
                message=message,
                notification_type=notification_type,
            )
            for student in recipients
        ]

        Notification.objects.bulk_create(
            notifications
        )

        return Response(
            {
                "success": True,
                "message": "Notification published successfully.",
                "recipient_count": len(notifications),
            },
            status=status.HTTP_201_CREATED,
        )