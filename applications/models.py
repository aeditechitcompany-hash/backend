from django.conf import settings
from django.db import models


class Application(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        OFFER_RECEIVED = "offer_received", "Offer Received"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="applications")
    university = models.ForeignKey("universities.University", on_delete=models.CASCADE, related_name="applications")
    course = models.ForeignKey("universities.Course", on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    intake = models.CharField(max_length=50, blank=True)
    applied_date = models.DateField(blank=True, null=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="handled_applications"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.user.email} -> {self.university.name} ({self.status})"


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=32, choices=Application.Status.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name_plural = "Application status histories"

    def __str__(self):
        return f"{self.application_id} -> {self.status}"
