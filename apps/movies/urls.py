from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, MovieViewSet, MovieScheduleViewSet

router = DefaultRouter()
router.register(r'genre', GenreViewSet, basename='genre')
router.register(r'movie', MovieViewSet, basename='movie')
router.register(r'movie-schedule', MovieScheduleViewSet, basename='movieschedule')

urlpatterns = [
    path('', include(router.urls))
]
