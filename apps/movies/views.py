from rest_framework import viewsets, permissions
from .models import Genre, Movie, MovieSchedule
from .serializers import GenreSerializer, MovieSerializer, MovieScheduleSerializer

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.select_related().prefetch_related('genres').all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]

class MovieScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovieSchedule.objects.select_related('movie').all()
    serializer_class = MovieScheduleSerializer
    permission_classes = [permissions.AllowAny]
