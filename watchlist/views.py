from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from movies.models import Watchlist, Movie
from rest_framework.exceptions import NotFound
from .serializers.common import WatchlistSerializer
import requests
from django.conf import settings

# Create your views here.
## WATCHLIST ROUTES 

class WatchlistIndex(APIView):
    permission_classes = [IsAuthenticated]

    # Display all movies in watchlist 
    def get(self, request):
        # filter Watchlist table to only show logged in users movies 
        watchlist = Watchlist.objects.filter(user = request.user.id)
        serializer = WatchlistSerializer(watchlist, many=True)
        return Response(serializer.data)


class WatchlistItemsView(APIView):
    permission_classes = [IsAuthenticated]
    # helper function 
    def get_watchlist_item(self, tmdb_id):
        try: 
            return Watchlist.objects.get(user=self.request.user, movie__tmdb_id=tmdb_id)
        except Watchlist.DoesNotExist:
            raise NotFound('Movie not in your watchlist ')

    # Create Watchlist by adding movie
    def post(self, request, pk):
        # get movie info from TMDB 
        API_KEY = settings.TMDB_API_KEY
        TMDB_BEARER_TOKEN = settings.TMDB_BEARER_TOKEN
        base_url = 'https://api.themoviedb.org/3/movie/'
        movie_id = pk
        headers = {
        "accept": "application/json",
        "Authorization": TMDB_BEARER_TOKEN}
        url = f'{base_url}{movie_id}?api_key={API_KEY}'
        tmdb_response = requests.get(url, headers=headers)
        data = tmdb_response.json()
        # print({'movie info': data})
        # get info needed based on Model 
        tmdb_id = data['id']
        title = data['title']
        poster = data['poster_path']
        release_date = data['release_date'][:4] # as i just want the year as integer 
        # retreive movie from TMDB database and save to Movie table
        movie, created = Movie.objects.get_or_create(tmdb_id=tmdb_id, defaults={'title': title, 'poster': poster, 'release_date': release_date})
        if created: 
            print('A new movie was added to table')
        else:
            print('Movie already added')
        # retrieve and save a movie instance to watchlist 
        watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, movie=movie, defaults={'is_watched': False})
        serializer = WatchlistSerializer(watchlist_item)
        if created:
            return Response({'Added to watchlist': serializer.data})
        else: 
            return Response({'message': 'Movie already in Watchlist'})
    
    # Remove movie from watchlist by marking as watched
    def patch(self, request, pk): 
        watchlist_item = self.get_watchlist_item(pk)
        # if watched, delete 
        if request.data.get('is_watched') is True:
            watchlist_item.delete()
            return Response({'message': 'Movie removed from your watchlist'})
        else: 
            # if not wachted, keep in watchlist 
            return Response({'message': 'Movie is not watched. Keep in watchlist'})
    
    # Delete movie from watchlist 
    def delete(self, request, pk):
        watchlist_item = self.get_watchlist_item(pk)
        watchlist_item.delete()
        return Response({'message': 'Movie was deleted'}, status=204)
