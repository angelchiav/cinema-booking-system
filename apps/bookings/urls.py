

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, BookedSeatViewSet, SeatReservationViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'booked-seats', BookedSeatViewSet, basename='bookedseat')
router.register(r'seat-reservations', SeatReservationViewSet, basename='seatreservation')

urlpatterns = [
    path('', include(router.urls)),
]