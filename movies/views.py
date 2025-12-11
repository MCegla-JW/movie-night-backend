from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import requests
from django.conf import settings

# Create your views here.

#URL: /movies 
# INDEX ROUTE

class MoviesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        API_KEY = settings.TMDB_API_KEY
        base_url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc"
        url = f'{base_url}?api_key={API_KEY}'
        headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3NmYyNWU3ZGI1ZjI2NGYwNjlmNDMyNzk1N2ZmYTkwNCIsIm5iZiI6MTc2NTQ0NDExNC45MzI5OTk4LCJzdWIiOiI2OTNhOGExMjBmYTYyYmI1YmFjZGYxNGMiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.6tyytW5sm59BRh4X0dC13LrEgbgRM2eCJCydz6DKel4"}
        response = requests.get(url, headers=headers)
        data = response.json().get('results',[])
        print(data)
        return Response({'movies': data})