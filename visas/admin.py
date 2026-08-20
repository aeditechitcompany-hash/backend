from django.contrib import admin
from .models import VisaApplication, VisaDocument


class VisaDocumentInline(admin.TabularInline):
    model = VisaDocument
    extra = 0


@admin.register(VisaApplication)
class VisaApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "country", "visa_type", "status", "application_date")
    list_filter = ("status", "country")
    inlines = [VisaDocumentInline]
