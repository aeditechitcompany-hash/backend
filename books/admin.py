from django.contrib import admin
from .models import (
    BookCategory,
    Book,
    BookProgress,
    Bookmark,
)
@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "author",
        "featured",
        "is_active",
        "uploaded_by",
        "total_views",
        "total_downloads",
        "created_at",
    )

    list_filter = (
        "category",
        "featured",
        "is_active",
    )

    search_fields = (
        "title",
        "author",
        "description",
    )

    readonly_fields = (
        "total_views",
        "total_downloads",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

@admin.register(BookProgress)
class BookProgressAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "book",
        "last_page",
        "percentage",
        "last_opened",
    )

    search_fields = (
        "student__user__email",
        "book__title",
    )

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "book",
        "page",
        "created_at",
    )

    search_fields = (
        "student__user__email",
        "book__title",
    )
# Register your models here.
