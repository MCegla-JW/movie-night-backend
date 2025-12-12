from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from .models import Party, PartyMovie
from rest_framework.exceptions import NotFound
from .serializers.common import PartySerializer, PartyMovieSerializer
from django.db.models import Q
import uuid
from movies.models import Watchlist

# Create your views here.
## PARTY ROUTES 

# INDEX ROUTE - show all parties filtered by created by user and where user is a member 

class PartyIndex(APIView):
    permission_classes = [IsAuthenticated]
    
    # Display all parties 
    def get(self, request):
        # display user created parties OR parties where user is a member 
        parties = Party.objects.filter(
            Q(creator = request.user.id) | 
            Q(members = request.user)).distinct()
        print(request.user.id)
        print(request.user)
        serializer = PartySerializer(parties, many=True)
        return Response(serializer.data, 200)
    
    def post(self, request): 
        serializer = PartySerializer(data=request.data)
        is_valid = serializer.is_valid(raise_exception=True)
        print(serializer._validated_data)
        # save created party
        created_party = serializer.save(creator = request.user, join_code = uuid.uuid4())
        # add creator as first party member 
        creator = request.user
        created_party.members.add(creator)
        # add movie to party movie 
        # get creators watchlist movies and filter and find one at random
        movie_to_add = Watchlist.objects.filter(user = request.user.id).order_by("?").first()
        if movie_to_add == None:
            return Response({'message': 'Watchlist empty. Add movies first'})
        print(movie_to_add)
        # create a party movie instance 
        # data from Party Movie model 
        data = {
        'party': created_party.id,
        'movie': movie_to_add.movie.id,  
        'added_by_user': creator.id
        }
        serializer_party_movie = PartyMovieSerializer(data=data)
        is_valid = serializer_party_movie.is_valid(raise_exception=True)
        party_movie = serializer_party_movie.save()
        updated_serializer = PartySerializer(created_party)
        return Response(updated_serializer.data, 201)


    # class PartyItemsView(APIView):
    #     permission_classes = [IsAuthenticated]

    #     # helper function 
    #     def get_party_item(self, pk):