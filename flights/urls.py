from rest_framework.routers import DefaultRouter
from .views import FlightBookingViewSet

router = DefaultRouter()
router.register(r"flight-bookings", FlightBookingViewSet, basename="flight-booking")

urlpatterns = router.urls
