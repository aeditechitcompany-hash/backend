from rest_framework.routers import DefaultRouter
from .views import BookViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r"",BookViewSet,basename="books")

urlpatterns = [
    path("", include(router.urls)),
]