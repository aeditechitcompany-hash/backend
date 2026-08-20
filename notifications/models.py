from django.conf import settings
from django.db import models


class NotificationTemplate(models.Model):
    key = models.CharField(max_length=100, unique=True)
    title_template = models.CharField(max_length=255)
    message_template = models.TextField()

    def __str__(self):
        return self.key


class Notification(models.Model):
    class Type(models.TextChoices):
        INFO = "info", "Info"
        SUCCESS = "success", "Success"
        WARNING = "warning", "Warning"
        ALERT = "alert", "Alert"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=16, choices=Type.choices, default=Type.INFO)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} -> {self.user.email}"
