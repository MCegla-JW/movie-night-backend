from rest_framework import serializers
from movies.models import Watchlist
from movies.serializers.common import MovieSerializer

class WatchlistSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'movie', 'is_watched', 'user',]
        ready_only_fields = ['user']