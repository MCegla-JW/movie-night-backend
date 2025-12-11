from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Create your views here.
## WATCHLIST ROUTES 

class WatchlistIndex(APIView):
    permission_classes = [IsAuthenticated]

    # Display all movies in watchlist 
    def get(self, request):
        return Response({'message': 'Hit Watchlist Index route'})


class WatchlistItemsView(APIView):
    permission_classes = [IsAuthenticated]

    # Create Watchlist by adding movie
    def post(self, request, pk):
        print(pk)
        return Response({'message': 'Hit Create Watchlist route'})
    
    # Remove movie from watchlist by marking as watched
    def patch(self, request, pk):
        return Response({'message': 'Hit remove movie from watchlist route by marking as watched'})
    
    # Delete movie from watchlist 
    def delete(self, request, pk):
        return Response({'message': 'Hit delete movie from watchlist route'})
