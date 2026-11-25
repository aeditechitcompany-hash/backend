
from django.contrib import admin
from django.utils import timezone

from .models import (
    BookCategory,
    Book,
    StudentBookAccess,
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
        "price",
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


@admin.register(StudentBookAccess)
class StudentBookAccessAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "book",
        "status",
        "approved_by",
        "approved_at",
        "expires_at",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
        "approved_at",
    )

    search_fields = (
        "student__user__email",
        "student__user__first_name",
        "student__user__last_name",
        "book__title",
        "payment_reference",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "student",
        "book",
        "approved_by",
    )

    actions = (
        "approve_selected",
        "revoke_selected",
        "mark_pending",
    )

    @admin.action(description="Approve selected book access")
    def approve_selected(self, request, queryset):
        now = timezone.now()

        for access in queryset:
            access.status = StudentBookAccess.Status.APPROVED
            access.approved_by = request.user
            access.approved_at = now
            access.save(
                update_fields=[
                    "status",
                    "approved_by",
                    "approved_at",
                    "updated_at",
                ]
            )

    @admin.action(description="Revoke selected book access")
    def revoke_selected(self, request, queryset):
        queryset.update(
            status=StudentBookAccess.Status.REVOKED,
            updated_at=timezone.now(),
        )

    @admin.action(description="Mark selected access as pending")
    def mark_pending(self, request, queryset):
        queryset.update(
            status=StudentBookAccess.Status.PENDING,
            approved_by=None,
            approved_at=None,
            updated_at=timezone.now(),
        )


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
