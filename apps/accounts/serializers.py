from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import (
    User, 
    UserProfile, 
    UserPreferences, 
    EmailVerificationToken,
    PasswordResetToken,
    UserSession,
    UserActivityLog
)

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    first_name = serializers.CharField(
        write_only=True,
        max_length=30
    )

    last_name = serializers.CharField(
        write_only=True,
        max_length=30
    )

    date_of_birth = serializers.DateField(
        required=True
    )

    phone = serializers.CharField(
        required=False,
        allow_blank=True
    )

    accept_terms = serializers.BooleanField(
        write_only=True,
        required=True
    )

    accept_privacy = serializers.BooleanField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password2', 'first_name', 'last_name',
            'date_of_birth', 'phone', 'preferred_language',
            'accept_terms', 'accept_privacy'
        ]

        extra_kwargs = {
            'preferred_language': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': "The passwords do not match"
            })
    
        if not attrs.get('accept_terms'):
            raise serializers.ValidationError({
                'accept_terms': 'You must accept the terms and conditions'
            })

        if not attrs.get('accept_privacy'):
            raise serializers.ValidationError({
                "accept_privacy": "You must accept the privacy policy."
            })
        
        attrs.pop('password2', None)
        attrs.pop('accept_terms', None)
        attrs.pop('accept_privacy', None)

        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    remember_me = serializers.BooleanField(
        required=False,
        default=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
        
            if not user:
                raise serializers.ValidationError({
                    'non_fields_error': 'Invalid email or password'
                })
            
            if not user.is_active:
                raise serializers.ValidationError({
                    'non_fields_error': 'Your account is disabled'
                })
            
            if not user.is_email_verified:
                raise serializers.ValidationError({
                    'non_fields_error': 'Please verify your email address before logging in'
                })
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError({
            'non_fields_error': 'Must include email and password'
        })
    
class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()
    is_adult = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'date_of_birth', 'age', 'is_adult',
            'preferred_language', 'is_email_verified', 'is_phone_verified',
            'date_joined', 'last_login'
        ]
        
        read_only_fields = [
            'id', 'email', 'is_email_verified', 'is_phone_verified',
            'date_joined', 'last_login'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()
    
class UserProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'gender', 'occupation', 'location',
            'emergency_contact_name', 'emergency_contact_phone'
        ]

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = [
            'email_notifications', 'sms_notifications', 'marketing_emails',
            'booking_reminders', 'reminder_time', 'preferred_seat_type',
            'preferred_cinema_location', 'accessibility_needs',
            'public_profile', 'share_movie_history'
        ]

    def validate_reminder_time(self, value):
        if value < 0 or value > 1440:
            return serializers.ValidationError(
                "Reminder time must be between 0 and 1440 minutes (24 hours)"
            )
        return value
    
class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Current password is incorrect"
            )
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password': 'New password do not match'
            })
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_emai(self, value):
        try:
            user = User.objects.get(email=value, is_active=True)

        except User.DoesNotExist:
            pass # Don't reveal if email exists for security reasons
        
        return value
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        write_only=True
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate_token(self, value):
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            if not reset_token.is_valid:
                raise serializers.ValidationError("Invalid or expired token.")
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")
        
        self.reset_token = reset_token
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs

    def save(self):
        user = self.reset_token.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Mark token as used
        self.reset_token.is_used = True
        self.reset_token.save()
        
        return user


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)

    def validate_token(self, value):
        try:
            verification_token = EmailVerificationToken.objects.get(token=value)
            if not verification_token.is_valid:
                raise serializers.ValidationError("Invalid or expired token.")
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")
        
        self.verification_token = verification_token
        return value

    def save(self):
        user = self.verification_token.user
        user.is_email_verified = True
        user.save()
        
        # Mark token as used
        self.verification_token.is_used = True
        self.verification_token.save()
        
        return user


class UserSessionSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = [
            'id', 'ip_address', 'location', 'device_type',
            'is_active', 'created_at', 'last_activity',
            'logged_out_at', 'duration', 'is_current'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity', 'logged_out_at']

    def get_duration(self, obj):
        duration = obj.duration
        return int(duration.total_seconds() / 60) if duration else None

    def get_is_current(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'session'):
            return obj.session_key == request.session.session_key
        return False


class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityLog
        fields = [
            'id', 'action', 'description', 'success',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserAccountSummarySerializer(serializers.ModelSerializer):
    profile = UserProfileDetailSerializer(read_only=True)
    preferences = UserPreferencesSerializer(read_only=True)
    total_bookings = serializers.SerializerMethodField()
    total_sessions = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()
    account_age_days = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'date_of_birth', 'preferred_language',
            'is_email_verified', 'is_phone_verified',
            'date_joined', 'last_login', 'profile', 'preferences',
            'total_bookings', 'total_sessions', 'last_activity',
            'account_age_days'
        ]
        read_only_fields = [
            'id', 'email', 'is_email_verified', 'is_phone_verified',
            'date_joined', 'last_login'
        ]

    def get_total_bookings(self, obj):
        return getattr(obj, 'bookings', obj.bookings).count()

    def get_total_sessions(self, obj):
        return obj.sessions.count()

    def get_last_activity(self, obj):
        last_session = obj.sessions.filter(is_active=True).first()
        return last_session.last_activity if last_session else obj.last_login

    def get_account_age_days(self, obj):
        from django.utils import timezone
        if obj.date_joined:
            delta = timezone.now() - obj.date_joined
            return delta.days
        return 0


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'date_of_birth',
            'preferred_language'
        ]

    def validate_phone(self, value):
        if value:
            # Reset phone verification if phone changes
            if self.instance and self.instance.phone != value:
                self.instance.is_phone_verified = False
        return value

    def update(self, instance, validated_data):
        phone = validated_data.get('phone')
        if phone and instance.phone != phone:
            instance.is_phone_verified = False
        
        return super().update(instance, validated_data)


class UserDeactivationSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    reason = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Optional reason for account deactivation"
    )
    feedback = serializers.CharField(
        required=False,
        max_length=1000,
        help_text="Optional feedback for service improvement"
    )

    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password is incorrect.")
        return value