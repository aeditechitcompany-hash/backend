from django.db import models


class Preferences(models.Model):
    class StudyLevel(models.TextChoices):
        BACHELOR = "bachelor", "Bachelor's"
        MASTERS = "masters", "Master's"
        PHD = "phd", "PhD"

    class Intake(models.TextChoices):
        SPRING = "spring", "Spring"
        SUMMER = "summer", "Summer"
        FALL = "fall", "Fall"
        WINTER = "winter", "Winter"

    student = models.OneToOneField("students.StudentProfile", on_delete=models.CASCADE, related_name="preferences")
    preferred_countries = models.ManyToManyField("countries.Country", blank=True, related_name="interested_students")
    preferred_universities = models.ManyToManyField("universities.University", blank=True, related_name="interested_students")
    preferred_study_level = models.CharField(max_length=32, choices=StudyLevel.choices, blank=True)
    preferred_courses = models.CharField(max_length=255, blank=True, help_text="Comma separated course interests")
    preferred_intake = models.CharField(max_length=16, choices=Intake.choices, blank=True)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Preferences({self.student.user.email})"
