from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import uuid
import string
import random

class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired')
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

    total_amount = models.DecimalField(
        "Total Amount",
        max_digits=8, 
        decimal_places=2
    )
    
    booking_status = models.CharField(
        "Booking Status",
        max_length=10,
        choices=BOOKING_STATUS_CHOICES,
        default='PENDING'
    )

    booking_time = models.DateTimeField(
        "Booking Time",
        auto_now_add=True
    )

    expires_at = models.DateTimeField("Expires At")
    
    confirmed_at = models.DateTimeField(
        "Confirmed At",
        null=True,
        blank=True
    )

    payment_method = models.CharField(
        "Payment Method",
        max_length=50,
        blank=True,
        null=True
    )
    
    payment_reference = models.CharField(
        "Payment Reference",
        max_length=100,
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        "Notes",
        blank=True,
        help_text="Internal notes about the booking"
    )

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Booking expires in 15 minutes by default
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-booking_time']

    def __str__(self):
        return f"Booking {self.booking_reference} by {self.user.email}"

    def is_expired(self):
        return timezone.now() > self.expires_at and self.booking_status == 'PENDING'

    def total_seats(self):
        return self.booked_seats.count()

    def seat_numbers(self):
        return [f"{seat.seat.row}{seat.seat.seat_number}" for seat in self.booked_seats.all()]

    def can_be_cancelled(self):
        if self.booking_status != 'CONFIRMED':
            return False
        
        # Can't cancel if movie has already started
        return self.movie_schedule.start_time > timezone.now()

    def calculate_total_amount(self):
        total = 0
        for booked_seat in self.booked_seats.all():
            total += booked_seat.seat.get_price_for_schedule(self.movie_schedule)
        return total

    def confirm_booking(self, payment_method=None, payment_reference=None):
        self.booking_status = 'CONFIRMED'
        self.confirmed_at = timezone.now()
        if payment_method:
            self.payment_method = payment_method
        if payment_reference:
            self.payment_reference = payment_reference
        self.save()

    def cancel_booking(self, reason=None):
        self.booking_status = 'CANCELLED'
        if reason:
            self.notes = f"Cancelled: {reason}"
        self.save()


class BookedSeat(models.Model):
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='booked_seats'
    )

    seat = models.ForeignKey(
        'movies.Seat',
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    price_paid = models.DecimalField(
        "Price Paid",
        max_digits=8,
        decimal_places=2,
        help_text="Actual price paid for this seat"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['booking', 'seat']

    def __str__(self):
        return f"Seat {self.seat.row}{self.seat.seat_number}"

    def save(self, *args, **kwargs):
        # Auto-calculate price if not provided
        if not self.price_paid:
            self.price_paid = self.seat.get_price_for_schedule(self.booking.movie_schedule)
        super().save(*args, **kwargs)


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
    
    seat = models.ForeignKey(
        'movies.Seat',
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    reserved_at = models.DateTimeField(
        "Reserved At",
        auto_now_add=True
    )

    reserved_until = models.DateTimeField("Reserved Until")

    # Session tracking to avoid conflicts
    session_key = models.CharField(
        "Session Key",
        max_length=40,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        if not self.reserved_until:
            self.reserved_until = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['movie_schedule', 'seat']

    def __str__(self):
        return f"Reserved seat {self.seat.row}{self.seat.seat_number} by {self.user.email}"

    def is_expired(self):
        """Check if reservation has expired"""
        return timezone.now() > self.reserved_until

    def extend_reservation(self, minutes=15):
        """Extend reservation by specified minutes"""
        self.reserved_until = timezone.now() + timedelta(minutes=minutes)
        self.save()


class BookingHistory(models.Model):
    """Track booking status changes"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('refunded', 'Refunded'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='history'
    )

    action = models.CharField(
        "Action",
        max_length=20,
        choices=ACTION_CHOICES
    )

    description = models.TextField(
        "Description",
        blank=True
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booking_actions'
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    metadata = models.JSONField(
        "Metadata",
        default=dict,
        blank=True
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.booking.booking_reference} - {self.action} at {self.timestamp}"