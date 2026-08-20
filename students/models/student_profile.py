import uuid
from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=16, choices=Gender.choices, blank=True, null=True)
    nationality = models.ForeignKey("countries.Country", on_delete=models.SET_NULL, null=True, blank=True, related_name="nationals")
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.ForeignKey("countries.Country", on_delete=models.SET_NULL, null=True, blank=True, related_name="residents")
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_completion_percentage = models.PositiveSmallIntegerField(default=0)
    assigned_counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_students"
    )

    mcq_access = models.BooleanField(
        default=False,
        help_text="Whether the student can access the MCQ module."
    )
    book_access = models.BooleanField(
            default=False,
            help_text="Whether the student can access the Books module."
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile({self.user.email})"
