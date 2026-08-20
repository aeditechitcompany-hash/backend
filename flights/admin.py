from django.contrib import admin
from .models import FlightBooking


@admin.register(FlightBooking)
class FlightBookingAdmin(admin.ModelAdmin):
    list_display = ("student", "airline", "flight_number", "departure_date", "status")
    list_filter = ("status", "airline")
