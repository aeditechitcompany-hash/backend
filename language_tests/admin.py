from django.contrib import admin
from .models import LanguageTest


@admin.register(LanguageTest)
class LanguageTestAdmin(admin.ModelAdmin):
    list_display = ("student", "test_type", "test_date", "overall_score", "is_verified")
    list_filter = ("test_type", "is_verified")
