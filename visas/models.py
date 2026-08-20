from django.db import models


class VisaApplication(models.Model):
    class Status(models.TextChoices):
        PREPARING = "preparing", "Preparing"
        SUBMITTED = "submitted", "Submitted"
        INTERVIEW_SCHEDULED = "interview_scheduled", "Interview Scheduled"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="visa_applications")
    application = models.ForeignKey(
        "applications.Application", on_delete=models.SET_NULL, null=True, blank=True, related_name="visa_applications"
    )
    country = models.ForeignKey("countries.Country", on_delete=models.CASCADE, related_name="visa_applications")
    visa_type = models.CharField(max_length=100, blank=True)
    application_date = models.DateField(blank=True, null=True)
    interview_date = models.DateField(blank=True, null=True)
    decision_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PREPARING)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Visa({self.student.user.email}, {self.country.name})"


class VisaDocument(models.Model):
    visa_application = models.ForeignKey(VisaApplication, on_delete=models.CASCADE, related_name="visa_documents")
    document = models.ForeignKey("documents.Document", on_delete=models.CASCADE, related_name="visa_links")

    class Meta:
        unique_together = ("visa_application", "document")

    def __str__(self):
        return f"{self.visa_application_id} - {self.document_id}"
