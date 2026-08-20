from django.db import models


class University(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey("countries.Country", on_delete=models.CASCADE, related_name="universities")
    city = models.ForeignKey("countries.City", on_delete=models.SET_NULL, null=True, blank=True, related_name="universities")
    website = models.URLField(blank=True)
    ranking = models.PositiveIntegerField(blank=True, null=True)
    logo = models.ImageField(upload_to="university_logos/", blank=True, null=True)
    description = models.TextField(blank=True)
    is_partner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Universities"

    def __str__(self):
        return self.name


class Course(models.Model):
    class DegreeLevel(models.TextChoices):
        UNDERGRADUATE = "undergraduate", "Undergraduate"
        POSTGRADUATE = "postgraduate", "Postgraduate"
        DOCTORATE = "doctorate", "Doctorate"
        DIPLOMA = "diploma", "Diploma"

    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="courses")
    name = models.CharField(max_length=255)
    degree_level = models.CharField(max_length=32, choices=DegreeLevel.choices)
    duration_months = models.PositiveIntegerField(blank=True, null=True)
    tuition_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, default="USD")
    language = models.CharField(max_length=50, blank=True, default="English")
    intake_months = models.CharField(max_length=100, blank=True, help_text="Comma separated e.g. September,January")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.university.name}"
