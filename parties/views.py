from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from .models import Party, PartyMovie, Vote
from rest_framework.exceptions import NotFound
from .serializers.common import PartySerializer, PartyMovieSerializer
from django.db.models import Q, Count, Max
import uuid
from movies.models import Watchlist
from django.shortcuts import get_object_or_404

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
    
    # Create a party
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
        if PartyMovie.objects.filter(party=created_party, movie=movie_to_add.movie).exists():
            return Response({'message': 'Cannot add duplicate movies. Movie aleady in party'})
        is_valid = serializer_party_movie.is_valid(raise_exception=True)
        party_movie = serializer_party_movie.save()
        updated_serializer = PartySerializer(created_party)
        return Response(updated_serializer.data, 201)


class PartyItemsView(APIView):
    permission_classes = [IsAuthenticated]

    # helper function 
    def get_party_item(self, pk):
        try:
            return Party.objects.get(pk=pk)
        except Party.DoesNotExist:
            raise NotFound('Party does not exist')
    
    # Get a single party
    def get(self, request, pk):
        party = self.get_party_item(pk)
        serializer = PartySerializer(party)
        return Response(serializer.data, 201)
    
    # Update a party
    def put(self, request, pk):
        party = self.get_party_item(pk)
        self.check_object_permissions(request, party)
        serializer = PartySerializer(data=request.data, instance=party)
        is_valid = serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    # Delete 
    def delete(self, request, pk):
        party = self.get_party_item(pk)
        self.check_object_permissions(request, party)
        party.delete()
        return Response({'message': 'Party was deleted successfully'}, 204)
    
# Join party 
# Path - /parties/<int:pk>/join/

class PartyJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, join_code):
        # party object 
        # pk is party id
        # verify party exists
        party = get_object_or_404(Party, join_code=join_code)
        print(party)
        print(party.members.all())
        print(party.members.exists())
        print(party.members.count())
        user_to_join = request.user
        users_in_party = party.members.filter(id = user_to_join.id).exists()
        print(users_in_party)
        # verify user member or not 
        if users_in_party:
            return Response({'message': 'Party member already exists'})
        party.members.add(user_to_join)
        movie_to_add = Watchlist.objects.filter(user = request.user.id).order_by("?").first()
        if not movie_to_add:
            return Response({'message': 'Watchlist empty. Add movies first'})
        party_movie, created = PartyMovie.objects.get_or_create(party=party, movie=movie_to_add.movie, defaults={'added_by_user': user_to_join})
        if not created:
            return Response({'message': 'Cannot add duplicate movies. Movie aleady in party'})
        return Response({'message': 'User joined party'})

        
class PartyMovieIndex(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Get party
        party = get_object_or_404(Party, pk=pk)
        print(party)
        # Get all party members 
        party_members = party.members.all()
        print(party_members)
        # Get all movies 
        party_movies = PartyMovie.objects.filter(party=party)
        serializer = PartyMovieSerializer(party_movies, many=True)
        return Response({'Movies in party': serializer.data})
    

class VotesIndexView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Get party
        party = get_object_or_404(Party, pk=pk)
        print(party)
        # Get all party members 
        party_members = party.members.all()
        print(party_members)
        # Get all movies in this party
        party_movies = PartyMovie.objects.filter(party=party)
        print(party_movies)
        # count votes for each movie
        for party_movie in party_movies:
            party_movie.num_votes = Vote.objects.filter(party=party, movie=party_movie.movie).count()
        # find highest vote count
        max_votes = 0
        if party_movies:
            max_votes = max(pm.num_votes for pm in party_movies)
        serializer = PartyMovieSerializer(party_movies, many=True, context={'max_votes': max_votes})
        return Response({'Movies in party': serializer.data})
    
class CastVotesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, party_id, movie_id):
        party = get_object_or_404(Party, id=party_id)
        party_movies = PartyMovie.objects.filter(party=party, movie_id=movie_id)
        if not party_movies:
            return Response({'message': 'This movie is not in this party'}, 400)
        voting_user = request.user
        print(party)
        print(party_movies)
        print(voting_user)
        vote, created = Vote.objects.get_or_create(user=voting_user, party=party, movie_id=movie_id)
        if not created:
            return Response({'Cannot vote twice on the same movie'})
        return Response({'message': 'You voted'})
    
    def delete(self, request, party_id, movie_id):
        party = get_object_or_404(Party, id=party_id)
        party_movies = PartyMovie.objects.filter(party=party)
        voting_user = request.user
        unvote = Vote.objects.filter(user=voting_user, party=party, movie_id=movie_id).exists()
        if unvote:
            vote_to_delete = Vote.objects.get(user=voting_user, party=party, movie_id=movie_id).delete()
            return Response({'message': 'Vote removed successfully'})
        return Response({'message': 'Already unvoted'})
