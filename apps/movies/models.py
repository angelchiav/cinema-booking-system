from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Cinema(models.Model):
    name = models.CharField(
        "Cinema Name",
        max_length=200
    )
    
    address = models.TextField("Address")
    
    city = models.CharField("City", max_length=100)
    
    phone = models.CharField(
        "Phone Number",
        max_length=20,
        blank=True
    )
    
    email = models.EmailField(
        "Contact Email",
        blank=True
    )
    
    is_active = models.BooleanField("Active", default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cinema"
        verbose_name_plural = "Cinemas"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.city}"

    def total_screens(self):
        return self.screens.count()

    def total_capacity(self):
        return sum(screen.total_seats() for screen in self.screens.all())


class Screen(models.Model):
    """Model to represent a movie screen/theater room"""
    SCREEN_TYPES = [
        ('standard', 'Standard'),
        ('imax', 'IMAX'),
        ('4dx', '4DX'),
        ('vip', 'VIP'),
        ('premium', 'Premium'),
    ]

    cinema = models.ForeignKey(
        Cinema,
        on_delete=models.CASCADE,
        related_name='screens',
        verbose_name="Cinema"
    )
    
    name = models.CharField("Screen Name", max_length=100)
    
    screen_number = models.PositiveIntegerField("Screen Number")
    
    screen_type = models.CharField(
        "Screen Type",
        max_length=20,
        choices=SCREEN_TYPES,
        default='standard'
    )
    
    total_rows = models.PositiveIntegerField(
        "Total Rows",
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    
    seats_per_row = models.PositiveIntegerField(
        "Seats per Row",
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    has_accessibility = models.BooleanField(
        "Wheelchair Accessibility",
        default=True
    )
    
    is_active = models.BooleanField("Active", default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Screen"
        verbose_name_plural = "Screens"
        unique_together = ['cinema', 'screen_number']
        ordering = ['cinema', 'screen_number']

    def __str__(self):
        return f"{self.cinema.name} - Screen {self.screen_number}"

    def clean(self):
        if self.cinema_id:
            existing = Screen.objects.filter(
                cinema=self.cinema,
                screen_number=self.screen_number
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError(
                    f'Screen {self.screen_number} already exists in {self.cinema.name}'
                )

    def total_seats(self):
        return self.seats.count()

    def available_seats_for_schedule(self, movie_schedule):
        """Get available seats for a specific schedule"""
        from apps.bookings.models import BookedSeat, SeatReservation
        from django.utils import timezone
        
        # Already booked/purchased seats
        booked_seats = BookedSeat.objects.filter(
            booking__movie_schedule=movie_schedule,
            booking__booking_status__in=['CONFIRMED', 'PENDING']
        ).values_list('seat__id', flat=True)
        
        # Temporarily reserved seats (last 15 minutes)
        reserved_seats = SeatReservation.objects.filter(
            movie_schedule=movie_schedule,
            reserved_until__gte=timezone.now()
        ).values_list('seat__id', flat=True)
        
        # Combine both sets
        unavailable_seat_ids = set(booked_seats) | set(reserved_seats)
        
        return self.seats.exclude(id__in=unavailable_seat_ids)


class SeatType(models.Model):
    """Seat types with different pricing"""
    name = models.CharField(
        "Type Name",
        max_length=50,
        unique=True
    )
    
    description = models.TextField("Description", blank=True)
    
    base_price = models.DecimalField(
        "Base Price",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    color_code = models.CharField(
        "Color Code",
        max_length=7,
        default='#4CAF50',
        help_text="Hexadecimal color code for UI"
    )
    
    is_premium = models.BooleanField("Is Premium", default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Seat Type"
        verbose_name_plural = "Seat Types"
        ordering = ['base_price']

    def __str__(self):
        return f"{self.name} (${self.base_price})"


class Seat(models.Model):
    """Individual seat model"""
    SEAT_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('blocked', 'Blocked'),
    ]

    screen = models.ForeignKey(
        Screen,
        on_delete=models.CASCADE,
        related_name='seats',
        verbose_name="Screen"
    )
    
    seat_type = models.ForeignKey(
        SeatType,
        on_delete=models.CASCADE,
        related_name='seats',
        verbose_name="Seat Type"
    )
    
    row = models.CharField("Row", max_length=5)
    
    seat_number = models.CharField("Seat Number", max_length=10)
    
    is_accessible = models.BooleanField(
        "Wheelchair Accessible",
        default=False
    )
    
    is_couple_seat = models.BooleanField(
        "Couple/Love Seat",
        default=False
    )
    
    status = models.CharField(
        "Status",
        max_length=20,
        choices=SEAT_STATUS,
        default='available'
    )
    
    # Visual position in the theater
    position_x = models.PositiveIntegerField(
        "Position X",
        help_text="X position in the theater layout"
    )
    
    position_y = models.PositiveIntegerField(
        "Position Y",
        help_text="Y position in the theater layout"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Seat"
        verbose_name_plural = "Seats"
        unique_together = [
            ['screen', 'row', 'seat_number'],
            ['screen', 'position_x', 'position_y']
        ]
        ordering = ['screen', 'row', 'seat_number']

    def __str__(self):
        return f"{self.screen} - {self.row}{self.seat_number}"

    def clean(self):
        # Validate seat is within screen limits
        if self.position_x > self.screen.seats_per_row:
            raise ValidationError('Position X exceeds seats per row')
        
        if self.position_y > self.screen.total_rows:
            raise ValidationError('Position Y exceeds total rows')

    def is_available_for_schedule(self, movie_schedule):
        """Check if seat is available for a schedule"""
        if self.status != 'available':
            return False
            
        from apps.bookings.models import BookedSeat, SeatReservation
        from django.utils import timezone
        
        # Check if booked
        is_booked = BookedSeat.objects.filter(
            seat=self,
            booking__movie_schedule=movie_schedule,
            booking__booking_status__in=['CONFIRMED', 'PENDING']
        ).exists()
        
        if is_booked:
            return False
        
        # Check temporary reservations
        is_reserved = SeatReservation.objects.filter(
            seat=self,
            movie_schedule=movie_schedule,
            reserved_until__gte=timezone.now()
        ).exists()
        
        return not is_reserved

    def get_price_for_schedule(self, movie_schedule):
        """Calculate seat price for a specific schedule"""
        base_price = self.seat_type.base_price
        
        # Here you can add dynamic pricing logic
        # For example, peak hours, weekends, etc.
        
        return base_price


class Genre(models.Model):
    name = models.CharField("Genre Name", max_length=50)

    def __str__(self):
        return self.name

    def movie_count(self):
        return self.movies.count()


class Movie(models.Model):
    CONTENT_RATINGS = [
        ('G', 'General Audiences'),
        ('PG', 'Parental Guidance'),
        ('PG-13', 'Parents Strongly Cautioned'),
        ('R', 'Restricted'),
        ('NC-17', 'Adults Only'),
    ]
    
    title = models.CharField("Movie Title", max_length=255)
    description = models.TextField("Description")
    duration_minutes = models.PositiveIntegerField("Duration (minutes)")
    release_date = models.DateField("Release Date")
    
    rating = models.DecimalField(
        "Rating",
        max_digits=3, 
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Rating from 0 to 10"
    )
    
    content_rating = models.CharField(
        "Content Rating",
        max_length=10,
        choices=CONTENT_RATINGS,
        default='G'
    )
    
    genres = models.ManyToManyField(
        Genre, 
        related_name='movies'
    )
    
    poster_image = models.URLField("Poster Image URL", blank=True)
    trailer_url = models.URLField("Trailer URL", blank=True)
    
    is_active = models.BooleanField("Active", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date']

    def __str__(self):
        return self.title

    def duration_in_hours(self):
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        return f"{hours}h {minutes}m"

    def genre_names(self):
        return [genre.name for genre in self.genres.all()]


class MovieSchedule(models.Model):
    movie = models.ForeignKey(
        Movie, 
        on_delete=models.CASCADE, 
        related_name='schedules'
    )
    
    screen = models.ForeignKey(
        Screen,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name="Screen"
    )
    
    start_time = models.DateTimeField("Start Time")
    end_time = models.DateTimeField("End Time")
    
    # Prices can vary per schedule
    base_price = models.DecimalField(
        "Base Price",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Base price multiplied by seat type price"
    )
    
    is_active = models.BooleanField("Active", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']
        unique_together = ['screen', 'start_time']

    def __str__(self):
        return f"{self.movie.title} - {self.screen} @ {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError('Start time must be before end time')
            
            overlapping = MovieSchedule.objects.filter(
                screen=self.screen,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(pk=self.pk)
            
            if overlapping.exists():
                raise ValidationError(
                    f'There is already a schedule in {self.screen} '
                    f'that overlaps with this time slot'
                )

    def is_upcoming(self):
        from django.utils import timezone
        return self.start_time > timezone.now()

    def duration_minutes(self):
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return self.movie.duration_minutes

    def available_seats_count(self):
        return self.screen.available_seats_for_schedule(self).count()

    def total_seats_count(self):
        return self.screen.total_seats()