from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta
import uuid

class User(AbstractUser):

    email = models.EmailField(
        "Email Address",
        unique=True,
        help_text="The email is required."
    )

    phone = models.CharField(
        "Phone Number",
        max_length=20,
        blank=True,
        null=True,
        validators= [
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in format: '+123456789.  19 digits allowed"
            )
        ]
    )

    date_of_birth = models.DateTimeField(
        "Date of Birth",
        null=True,
        blank=True,
        help_text="Required for age verification in certain movies"
    )

    is_email_verified = models.BooleanField(
        "Email Verified",
        default=False
    )

    is_phone_verified = models.BooleanField(
        "Phone Verified",
        default=False
    )

    preferred_language = models.CharField(
        "Preferred Language",
        max_length=10,
        choices=[
            ('en', 'English'),
            ('es', 'Spanish')
        ],
        default='en'
    )

    created_at = models.DateTimeField(
        "Created at",
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        "Last Update",
        auto_now=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name()} - ({self.email})"
    
    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def is_adult(self):
        return self.age and self.age >= 18
    
    def can_watch_rated_content(self, content_rating):
        age_restrictions = {
            'G': 0,
            'PG': 0,
            'PG-13': 13,
            'R': 17,
            'NC-17': 18
        }
        if content_rating not in age_restrictions:
            return True
        
        required_age = age_restrictions[content_rating]
        return self.age and self.age >= required_age
    
class UserProfile(models.Model):

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )

    bio = models.TextField(
        "Biography",
        max_length=500,
        blank=True,
        help_text="Optional bio or description (500 characters)"
    )

    avatar = models.ImageField(
        "Profile Picture",
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text="Optional"
    )

    gender = models.CharField(
        "Gender",
        max_length=10,
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
            ('P', 'Prefer not to say')
        ],
        blank=True,
        null=True
    )

    location = models.CharField(
        "City or general location",
        max_length=100,
        blank=True,
        help_text="Optional"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.email} - Profile"
    
class UserPreferences(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="preferences"
    )

    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive booking confirmations and updates via email"
    )

    sms_notifications = models.BooleanField(
        default=True,
        help_text="Receive booking confirmations and updates via SMS"
    )

    marketing_emails = models.BooleanField(
        default=False,
        help_text="Receive promotional emails and movie recommendations"
    )

    booking_reminders = models.BooleanField(
        default=True,
        help_text="Receive reminders before movie showtime"
    )

    reminder_time = models.IntegerField(
        default=60,
        help_text="Minutes before showtime to send reminder (default: 60 minutes)"
    )

    preferred_seat_type = models.CharField(
        max_length=20,
        choices=[
            ('any', 'Any'),
            ('aisle', 'Aisle'),
            ('center', 'Center'),
            ('back', 'Back rows'),
            ('front', 'Front rows'),
        ],
        default='any'
    )
    preferred_cinema_location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Preferred cinema location or area"
    )
    accessibility_needs = models.TextField(
        blank=True,
        help_text="Any accessibility requirements or needs"
    )
    
    public_profile = models.BooleanField(
        default=False,
        help_text="Make profile visible to other users"
    )
    share_movie_history = models.BooleanField(
        default=False,
        help_text="Allow movie history to be visible to friends"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"{self.user.email} - Preferences"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification_tokens'
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'

    def __str__(self):
        return f"Email verification for {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expires in 24 hours
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if token is valid (not expired and not used)"""
        return not self.is_expired and not self.is_used


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'

    def __str__(self):
        return f"Password reset for {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expires in 1 hour
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if token is valid (not expired and not used)"""
        return not self.is_expired and not self.is_used


class UserSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Approximate location based on IP"
    )
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('desktop', 'Desktop'),
            ('mobile', 'Mobile'),
            ('tablet', 'Tablet'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    logged_out_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'

    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.created_at}"

    def logout(self):
        """Mark session as logged out"""
        self.is_active = False
        self.logged_out_at = timezone.now()
        self.save()

    @property
    def duration(self):
        """Calculate session duration"""
        end_time = self.logged_out_at or timezone.now()
        return end_time - self.created_at


class UserActivityLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    action = models.CharField(
        max_length=50,
        choices=[
            ('login', 'Login'),
            ('logout', 'Logout'),
            ('password_change', 'Password Change'),
            ('profile_update', 'Profile Update'),
            ('email_change', 'Email Change'),
            ('booking_created', 'Booking Created'),
            ('booking_cancelled', 'Booking Cancelled'),
            ('payment_completed', 'Payment Completed'),
            ('account_deleted', 'Account Deleted'),
        ]
    )
    description = models.TextField(
        blank=True,
        help_text="Additional details about the action"
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField(
        default=True,
        help_text="Whether the action was successful"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the action"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.created_at}"