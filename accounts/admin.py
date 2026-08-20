from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, OTP, LoginHistory, PasswordResetToken, Role, FeaturePermission, UserRole


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("email", "username", "role","province","district","street_address", "is_email_verified", "is_active", "is_staff")
    list_filter = ("role","province","district","street_address", "is_email_verified", "is_active", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Extra", {"fields": ("phone_number", "role","province","district","street_address", "profile_picture", "is_email_verified", "is_phone_verified", "is_active_student")}),
    )


admin.site.register(OTP)
admin.site.register(LoginHistory)
admin.site.register(PasswordResetToken)
admin.site.register(Role)
admin.site.register(FeaturePermission)
admin.site.register(UserRole)
