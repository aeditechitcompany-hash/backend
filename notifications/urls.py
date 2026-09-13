from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationTemplateViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"notification-templates", NotificationTemplateViewSet, basename="notification-template")

urlpatterns = router.urls

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    NotificationViewSet,
    NotificationTemplateViewSet,
    register_device_token,
)

router = DefaultRouter()

router.register(
    r"notifications",
    NotificationViewSet,
    basename="notification",
)

router.register(
    r"notification-templates",
    NotificationTemplateViewSet,
    basename="notification-template",
)

urlpatterns = router.urls

urlpatterns += [
    path(
        "device-token/",
        register_device_token,
        name="register-device-token",
    ),
]