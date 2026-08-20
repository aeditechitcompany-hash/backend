from django.db import models


class FlightBooking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        BOOKED = "booked", "Booked"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="flight_bookings")
    airline = models.CharField(max_length=150, blank=True)
    flight_number = models.CharField(max_length=50, blank=True)
    departure_airport = models.CharField(max_length=150)
    arrival_airport = models.CharField(max_length=150)
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField(blank=True, null=True)
    booking_reference = models.CharField(max_length=100, blank=True)
    ticket_file = models.FileField(upload_to="flight_tickets/", blank=True, null=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-departure_date"]

    def __str__(self):
        return f"{self.student.user.email} - {self.flight_number}"
