
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .storage import SupabaseBookStorage


class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    category = models.ForeignKey(
        BookCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="books",
    )

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Book price in NPR.",
    )

    cover = models.ImageField(
        upload_to="books/covers/",
        blank=True,
        null=True,
    )

    pdf = models.FileField(
        upload_to="books/pdfs/",
        storage=SupabaseBookStorage(),
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    total_views = models.PositiveIntegerField(default=0)
    total_downloads = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class StudentBookAccess(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REVOKED = "revoked", "Revoked"

    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="book_access_records",
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="student_access_records",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_book_accesses",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank for access without an expiry date.",
    )

    payment_reference = models.CharField(
        max_length=255,
        blank=True,
    )

    admin_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "book"],
                name="unique_student_book_access",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.user.email} - {self.book.title} ({self.status})"

    @property
    def is_valid(self):
        return (
            self.status == self.Status.APPROVED
            and (
                self.expires_at is None
                or self.expires_at > timezone.now()
            )
        )


class BookProgress(models.Model):
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
    )

    last_page = models.PositiveIntegerField(default=1)

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    last_opened = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "book")


class Bookmark(models.Model):
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
    )

    page = models.PositiveIntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
