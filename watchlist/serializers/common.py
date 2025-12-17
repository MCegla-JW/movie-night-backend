from rest_framework import serializers
from movies.models import Watchlist
from movies.serializers.common import MovieSerializer

class WatchlistSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True) # nested movie data
    
    class Meta:
        model = Watchlist
        fields = ['id', 'movie', 'is_watched', 'user',]
        read_only_fields = ['user']