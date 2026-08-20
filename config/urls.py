from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView,SpectacularSwaggerView,SpectacularRedocView,)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui",
    ),
    path("api/redoc/",SpectacularRedocView.as_view(url_name="schema"), name="redoc",
    ),
    path("api/accounts/", include("accounts.urls")),
    path("api/students/", include("students.urls")),
    path("api/", include("countries.urls")),
    path("api/", include("universities.urls")),
    path("api/", include("documents.urls")),
    path("api/", include("applications.urls")),
    path("api/", include("interviews.urls")),
    path("api/", include("language_tests.urls")),
    path("api/", include("visas.urls")),
    path("api/", include("flights.urls")),
    path("api/", include("notifications.urls")),
    path("api/", include("process.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/", include("reports.urls")),
    path("api/mcq/", include("mcq.urls")),
    path("api/books/", include("books.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
