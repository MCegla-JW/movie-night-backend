from django.db import models

# Create your models here.
class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)
    poster = models.URLField(blank=True, null=True)
    release_date = models.DateField()

def __str__(self):
    return self.title

class Watchlist(models.Model):
    user = models.ForeignKey(
        to='users.User',
        related_name='watchlist',
        on_delete=models.CASCADE
    )
    movie = models.ForeignKey(
        to='movies.Movie',
        related_name='watchlist',
        on_delete=models.CASCADE
    )
    is_watched = models.BooleanField(default=False)

def __str__(self):
    return f'{self.user.username} added {self.movie.title} to watchlist'