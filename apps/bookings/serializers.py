

from django.utils import timezone
from rest_framework import serializers
from .models import Booking, BookedSeat, SeatReservation



class BookedSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedSeat
        fields = ['id', 'seat_number', 'row']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_seat_number(self, value):
        if not value:
            raise serializers.ValidationError("Seat number is required.")
        return value

    def validate_row(self, value):
        if not value:
            raise serializers.ValidationError("Row is required.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    booked_seats = BookedSeatSerializer(many=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'movie_schedule',
            'booking_reference',
            'total_amount',
            'booking_status',
            'booking_time',
            'expires_at',
            'confirmed_at',
            'booked_seats',
        ]

    def create(self, validated_data):
        booked_seats_data = validated_data.pop('booked_seats', [])
        booking = Booking.objects.create(**validated_data)
        for seat_data in booked_seats_data:
            BookedSeat.objects.create(booking=booking, **seat_data)
        return booking

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['user'] = instance.user.email
        rep['movie_schedule'] = str(instance.movie_schedule)
        return rep


class SeatReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatReservation
        fields = [
            'id',
            'user',
            'movie_schedule',
            'seat_number',
            'row',
            'reserved_at',
            'reserved_until',
        ]

    def validate(self, attrs):
        existing = SeatReservation.objects.filter(
            movie_schedule=attrs['movie_schedule'],
            seat_number=attrs['seat_number'],
            row=attrs['row'],
            reserved_until__gte=timezone.now()
        ).exists()
        if existing:
            raise serializers.ValidationError("Seat is already reserved.")
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['user'] = instance.user.email
        rep['movie_schedule'] = str(instance.movie_schedule)
        return rep