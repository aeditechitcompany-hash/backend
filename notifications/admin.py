from django.contrib import admin
from .models import Notification, NotificationTemplate

admin.site.register(NotificationTemplate)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
