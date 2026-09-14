from .models import Notification
from .firebase_service import send_push_notification


def create_notification(
    *,
    user,
    title,
    message,
    notification_type=Notification.Type.INFO,
):
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
    )

    send_push_notification(
        user=user,
        title=title,
        message=message,
    )

    return notification