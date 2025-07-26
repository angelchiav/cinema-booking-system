
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Booking, BookedSeat, SeatReservation
from .serializers import BookingSerializer, BookedSeatSerializer, SeatReservationSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()
        booking.booking_status = "CANCELLED"
        booking.save()
        return Response({"status": "Booking cancelled"}, status=status.HTTP_200_OK)


class BookedSeatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookedSeat.objects.all()
    serializer_class = BookedSeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookedSeat.objects.filter(booking__user=self.request.user)


class SeatReservationViewSet(viewsets.ModelViewSet):
    queryset = SeatReservation.objects.all()
    serializer_class = SeatReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return SeatReservation.objects.filter(user=self.request.user)
