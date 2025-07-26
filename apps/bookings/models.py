from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

class Booking(models.Model):
    BOOKING_STATUS_CHOICE = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled')
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )

    movie_schedule = models.ForeignKey(
        'movies.MovieSchedule',
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    booking_reference = models.CharField(
        max_length=32, 
        unique=True
    )

    total_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2
    )
    
    booking_status = models.CharField(
        max_length=10,
        choices=BOOKING_STATUS_CHOICE,
        default='PENDING'
    )

    booking_time = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Booking {self.booking_reference} by {self.user.email}"

class BookedSeat(models.Model):
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='booked_seats'
    )

    seat_number = models.CharField(
        max_length=10
    )

    row = models.CharField(
        max_length=5
    )

    def __str__(self):
        return f"Seat {self.row}{self.seat_number} for booking {self.booking.booking_reference}"

class SeatReservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='seat_reservations'
    )

    movie_schedule = models.ForeignKey(
        'movies.MovieSchedule',
        on_delete=models.CASCADE,
        related_name='seat_reservations'
    )
    seat_number = models.CharField(
        max_length=10
    )

    row = models.CharField(
        max_length=5
    )

    reserved_at = models.DateTimeField(
        auto_now_add=True
    )

    reserved_until = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.reserved_until:
            self.reserved_until = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserved seat {self.row}{self.seat_number} by {self.user.email}"