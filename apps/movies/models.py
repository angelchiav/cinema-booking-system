from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def movie_count(self):
        return self.movies.count()


class Movie(models.Model):
    title = models.CharField(
        max_length=255
    )

    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    release_date = models.DateField()
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1
    )

    genres = models.ManyToManyField(
        Genre, 
        related_name='movies'
    )

    poster_image = models.URLField(
        blank=True
    )

    def __str__(self):
        return self.title

    def duration_in_hours(self):
        return round(self.duration_minutes / 60, 2)

    def genre_names(self):
        return [genre.name for genre in self.genres.all()]


class MovieSchedule(models.Model):
    movie = models.ForeignKey(
        Movie, 
        on_delete=models.CASCADE, 
        related_name='schedules'
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    screen_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.movie.title} @ {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def is_upcoming(self):
        from django.utils import timezone
        return self.start_time > timezone.now()

    def duration(self):
        return (self.end_time - self.start_time).total_seconds() / 60