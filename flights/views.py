from rest_framework import viewsets
from .models import FlightBooking
from .serializers import FlightBookingSerializer


class FlightBookingViewSet(viewsets.ModelViewSet):
    queryset = FlightBooking.objects.select_related("student").all()
    serializer_class = FlightBookingSerializer
    filterset_fields = ["student", "status"]
