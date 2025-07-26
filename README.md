# Cinema Booking System API

A comprehensive full-stack API for movie ticket reservations featuring real-time seat selection, secure user management, and booking administration. Built with Django REST Framework.

## Features

### Core Features
- **User Management**: Custom user model with email verification and profile management
- **Movie Catalog**: Complete movie database with genres, schedules, and ratings
- **Seat Reservation**: Real-time seat selection with temporary holds (15 minutes)
- **Booking System**: Comprehensive booking management with status tracking
- **Security**: JWT authentication with session management and activity logging

### Advanced Features
- **User Preferences**: Personalized settings for notifications and seat preferences
- **Age Verification**: Content rating validation for age-restricted movies
- **Activity Logging**: Complete audit trail of user actions
- **Session Management**: Device tracking and session control
- **Profile System**: Rich user profiles with avatars and preferences

## Tech Stack

- **Backend**: Django 5.2.4 + Django REST Framework 3.16.0
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: JWT with djangorestframework-simplejwt
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Image Processing**: Pillow for user avatars

## 📁 Project Structure

```
cinema-booking-system/
├── apps/
│   ├── accounts/          # User management, authentication, profiles
│   ├── bookings/          # Booking system, seat reservations
│   └── movies/            # Movie catalog, schedules, genres
├── config/                # Django settings and configuration
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/angelchiav/cinema-booking-system.git
   cd cinema-booking-system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### Main Endpoints

#### Authentication
```
POST /api/accounts/register/           # User registration
POST /api/accounts/login/              # User login
POST /api/accounts/token/refresh/      # Refresh JWT token
```

#### User Management
```
GET    /api/accounts/users/                    # User profile
PUT    /api/accounts/users/{id}/               # Update profile
GET    /api/accounts/users/account_summary/    # Account summary
GET    /api/accounts/users/{id}/booking-history/  # Booking history
```

#### Movies
```
GET /api/movies/movie/              # List all movies
GET /api/movies/movie/{id}/         # Movie details
GET /api/movies/genre/              # List genres
GET /api/movies/movie-schedule/     # Movie schedules
```

#### Bookings
```
GET    /api/bookings/bookings/                 # User's bookings
POST   /api/bookings/bookings/                 # Create booking
POST   /api/bookings/bookings/{id}/cancel/     # Cancel booking
GET    /api/bookings/seat-reservations/        # Seat reservations
POST   /api/bookings/seat-reservations/        # Reserve seats
```

## Database Models

### Core Models

#### User Model
- Custom user model extending Django's AbstractUser
- Email-based authentication
- Phone verification support
- Age verification for content rating
- Preferred language settings

#### Movie System
- **Movie**: Title, description, duration, rating, genres
- **Genre**: Movie categorization
- **MovieSchedule**: Screening times and screen assignments

#### Booking System
- **Booking**: Complete booking with reference, status, and expiration
- **BookedSeat**: Individual seat assignments
- **SeatReservation**: Temporary seat holds (15-minute expiration)

### Example API Requests

#### User Registration
```json
POST /api/accounts/register/
{
    "email": "user@example.com",
    "password": "securepassword123",
    "password2": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "phone": "+1234567890",
    "accept_terms": true,
    "accept_privacy": true
}
```

#### Create Booking
```json
POST /api/bookings/bookings/
{
    "movie_schedule": 1,
    "total_amount": "25.50",
    "booked_seats": [
        {"seat_number": "A1", "row": "A"},
        {"seat_number": "A2", "row": "A"}
    ]
}
```

## Features in Development

### Payment Integration: Stripe/PayPal integration
### Email Notifications: Booking confirmations and reminders
### Advanced Seat Management: Theater layout configuration
### Mobile App: React Native frontend companion
### Admin Dashboard: Comprehensive management interface
### Analytics: Booking and revenue analytics
