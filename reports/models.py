from django.conf import settings
from django.db import models


class Report(models.Model):
    class ReportType(models.TextChoices):
        STUDENTS = "students", "Students"
        APPLICATIONS = "applications", "Applications"
        VISAS = "visas", "Visas"
        FINANCIAL = "financial", "Financial"
        CUSTOM = "custom", "Custom"

    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=32, choices=ReportType.choices)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="reports")
    filters = models.JSONField(blank=True, null=True)
    file = models.FileField(upload_to="reports/", blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.name} ({self.report_type})"
