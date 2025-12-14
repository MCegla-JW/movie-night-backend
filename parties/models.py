from django.db import models

# Create your models here.
class Party(models.Model):
    title = models.CharField(max_length=100, unique=True)
    join_code = models.CharField(max_length=100, unique=True)
    date = models.DateField()
    creator = models.ForeignKey(
        to='users.User',
        related_name='parties_created',
        on_delete=models.CASCADE
    )
    members = models.ManyToManyField(
        to='users.User',
        related_name='parties'
    )
    winning_movie = models.ForeignKey(
        to='movies.Movie',
        null=True,
        blank=True,
        on_delete=models.SET_NULL, 
        related_name='won_parties'
    )

    def __str__(self):
        return self.title


class PartyMovie(models.Model):
    party = models.ForeignKey(
        to='Party',
        related_name='party_movies',
        on_delete=models.CASCADE
    )
    movie = models.ForeignKey(
        to='movies.Movie',
        related_name='party_movies',
        on_delete=models.CASCADE
    )
    added_by_user = models.ForeignKey(
        to='users.User',
        related_name='party_movies',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('party', 'movie')

    def __str__(self):
        return f'{self.movie.title} in {self.party.title}'


class Vote(models.Model):
    user = models.ForeignKey(
        to='users.User',
        related_name='votes',
        on_delete=models.CASCADE
    )
    party = models.ForeignKey(
        to='Party',
        related_name='votes',
        on_delete=models.CASCADE
    )
    movie = models.ForeignKey(
        to='movies.Movie',
        related_name='votes',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['user', 'party']

    def __str__(self):
         return f'{self.user.username} voted for {self.movie.title} in {self.party.title}'