from rest_framework import serializers
from .models import Genre, Movie, MovieSchedule

class GenreSerializer(serializers.ModelSerializer):
    movie_count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['id', 'name', 'movie_count']

    def get_movie_count(self, obj):
        return obj.movie_count()


class MovieSerializer(serializers.ModelSerializer):
    genre_names = serializers.SerializerMethodField()
    duration_in_hours = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id',
            'title',
            'description',
            'duration_minutes',
            'duration_in_hours',
            'release_date',
            'rating',
            'genre_names',
            'poster_image'
        ]

    def get_genre_names(self, obj):
        return obj.genre_names()

    def get_duration_in_hours(self, obj):
        return obj.duration_in_hours()


class MovieScheduleSerializer(serializers.ModelSerializer):
    is_upcoming = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    movie_title = serializers.CharField(source='movie.title', read_only=True)

    class Meta:
        model = MovieSchedule
        fields = [
            'id', 
            'movie', 
            'movie_title', 
            'start_time', 
            'end_time', 
            'screen_number', 
            'is_upcoming', 
            'duration_minutes'
        ]

    def get_is_upcoming(self, obj):
        return obj.is_upcoming()

    def get_duration_minutes(self, obj):
        return int(obj.duration())