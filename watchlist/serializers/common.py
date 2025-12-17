from rest_framework import serializers
import requests
import os
from movies.models import Watchlist

class WatchlistSerializer(serializers.ModelSerializer):
    movie_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Watchlist
        fields = ['id', 'movie', 'is_watched', 'user', 'movie_details']
    
    def get_movie_details(self, obj):
        """Fetch full movie details from TMDB"""
        try:
            api_key = os.environ.get('TMDB_API_KEY')
            # Use obj.movie.tmdb_id instead of obj.movie
            tmdb_id = obj.movie.tmdb_id
            print(f"API Key exists: {bool(api_key)}")
            print(f"Fetching movie TMDB ID: {tmdb_id}")
            
            response = requests.get(
                f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}'
            )
            print(f"TMDB Response status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"TMDB Error: {response.text}")
                return None
        except Exception as e:
            print(f"Error fetching movie details: {e}")
            return None