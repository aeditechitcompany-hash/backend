from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Education(models.Model):
    class DegreeLevel(models.TextChoices):
        HIGH_SCHOOL = "high_school", "High School"
        DIPLOMA = "diploma", "Diploma"
        BACHELOR = "bachelor", "Bachelors"
        MASTER = "master", "Masters"
        PHD = "phd", "PHD"

    class GpaScale(models.TextChoices):
        GPA_4 = "4.0", "Out of 4.0"
        PERCENTAGE = "100", "Percentage"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="education_history")
    degree_level = models.CharField(max_length=32, choices=DegreeLevel.choices)
    institution_name = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey("countries.Country", on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, help_text="GPA / Percentage / Grade")
    is_completed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], 
        help_text="Numeric GPA/percentage value")
    gpa_scale = models.CharField(
        max_length=10, choices=GpaScale.choices, blank=True, null=True,
        help_text="What scale the `gpa` value is on, e.g. out of 4.0 or a percentage"
    )
    passout_year = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1950), MaxValueValidator(2100)],
        help_text="Year this qualification was/will be completed"
    )

    class Meta:
        ordering = ["-passout_year", "-end_date"]

    def __str__(self):
        return f"{self.institution_name} ({self.degree_level})"
