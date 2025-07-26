from rest_framework import viewsets, permissions
from .models import (
    User,
    UserProfile
)
from .serializers import (
    UserProfileSerializer,
    UserUpdateSerializer,
    UserAccountSummarySerializer,
    UserProfileDetailSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.bookings.models import Booking, SeatReservation
from apps.bookings.serializers import BookingSerializer, SeatReservationSerializer
from django.utils import timezone


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        elif self.action == 'account_summary':
            return UserAccountSummarySerializer
        return UserProfileSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=user.pk)
    
    @action(detail=False, methods=['get'], url_path='account_summary')
    def account_summary(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=204)

    @action(detail=True, methods=['get'], url_path='booking-history')
    def booking_history(self, request, pk=None):
        user = self.get_object()
        bookings = Booking.objects.filter(user=user).select_related('movie_schedule', 'movie_schedule__movie')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='active-seat-reservations')
    def active_seat_reservations(self, request, pk=None):
        user = self.get_object()
        now = timezone.now()
        reservations = SeatReservation.objects.filter(user=user, reserved_until__gte=now)
        serializer = SeatReservationSerializer(reservations, many=True)
        return Response(serializer.data)
    
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def perform_create(self):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=204)