from django.contrib import admin
from .models import Country, City


class CityInline(admin.TabularInline):
    model = City
    extra = 0


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "currency", "is_active")
    search_fields = ("name", "code")
    inlines = [CityInline]


admin.site.register(City)
