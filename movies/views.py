from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import requests
from django.conf import settings

# Create your views here.

#URL: /movies 
# INDEX ROUTE - show popular movies - MOVIE INDEX

class MoviesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        search_query = request.GET.get('search', '')
        API_KEY = settings.TMDB_API_KEY
        TMDB_BEARER_TOKEN = settings.TMDB_BEARER_TOKEN
        base_url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"
        search_url = "https://api.themoviedb.org/3/search/movie"
        headers = {
        "accept": "application/json",
        "Authorization": TMDB_BEARER_TOKEN}
        if search_query:
            url = f'{search_url}?api_key={API_KEY}&query={search_query}'
        else:
            url = f'{base_url}&api_key={API_KEY}'
        print({'search_query': search_query})
        print({'URL': url})
        response = requests.get(url, headers=headers)
        print({'response': response.status_code})
        print({'response': response.json()})
        data = response.json().get('results',[])
        print(data)
        return Response({'movies': data, 'search': search_query}, status=200)
    
