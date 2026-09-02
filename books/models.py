
import uuid
from django.db import models
from django.conf import settings
from .storage import SupabaseBookStorage

class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True)

    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    category = models.ForeignKey(
        BookCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="books"
    )

    title = models.CharField(max_length=255)

    author = models.CharField(max_length=255, blank=True)

    description = models.TextField(blank=True)

    cover = models.ImageField(
        upload_to="books/covers/",
        blank=True,
        null=True
    )

    pdf = models.FileField(
    upload_to="books/pdfs/",
    storage=SupabaseBookStorage(),
)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    featured = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    total_views = models.PositiveIntegerField(default=0)

    total_downloads = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class BookProgress(models.Model):

    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    last_page = models.PositiveIntegerField(default=1)

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    last_opened = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "book")

class Bookmark(models.Model):

    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    page = models.PositiveIntegerField()

    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
