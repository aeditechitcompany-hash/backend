from django.db import models


class LanguageTest(models.Model):
    class TestType(models.TextChoices):
        IELTS = "ielts", "IELTS"
        TOEFL = "toefl", "TOEFL"
        PTE = "pte", "PTE"
        DUOLINGO = "duolingo", "Duolingo English Test"
        OTHER = "other", "Other"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="language_tests")
    test_type = models.CharField(max_length=16, choices=TestType.choices)
    test_date = models.DateField()
    overall_score = models.DecimalField(max_digits=5, decimal_places=2)
    score_breakdown = models.JSONField(blank=True, null=True, help_text="e.g. listening/reading/writing/speaking")
    certificate = models.ForeignKey(
        "documents.Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="language_test_certificates"
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-test_date"]

    def __str__(self):
        return f"{self.get_test_type_display()} - {self.student.user.email}"
