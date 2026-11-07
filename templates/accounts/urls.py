from django.urls import path
from . import views

urlpatterns = [
    # Keep your existing URLs

    path(
        "delete-account/",
        views.delete_account_request,
        name="delete_account_request"
    ),
]