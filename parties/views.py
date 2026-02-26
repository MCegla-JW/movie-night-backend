from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from .models import Party, PartyMovie, Vote
from rest_framework.exceptions import NotFound
from .serializers.common import PartySerializer, PartyMovieSerializer
from django.db.models import Q
import uuid
from movies.models import Watchlist
from django.shortcuts import get_object_or_404
import random

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
        movie_to_add, created = PartyMovie.objects.get_or_create(party=created_party, movie=movie_to_add.movie, defaults={'added_by_user': request.user})
        # is_valid = serializer_party_movie.is_valid(raise_exception=True)
        # movie_to_add = serializer_party_movie.save()
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
        if users_in_party == True:
            print('User already in Party')
            return Response({'message': 'Party member already exists', 'party_id': party.id})
        party.members.add(user_to_join)
        print('Member added!')
        movie_to_add = Watchlist.objects.filter(user = request.user.id).order_by("?").first()
        if not movie_to_add:
            return Response({'message': 'Watchlist empty. Add movies first', 'party_id': party.id})
        party_movie, created = PartyMovie.objects.get_or_create(party=party, movie=movie_to_add.movie, defaults={'added_by_user': user_to_join})
        print(movie_to_add.movie)
        print(party_movie)
        if not created:
            return Response({'message': 'Cannot add duplicate movies. Movie aleady in party', 'party_id': party.id})
        serializer = PartySerializer(party)
        return Response({'message': 'User joined party', 'party_id': party.id})

        
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
        # find all movies with max votes
        tied_movies = [pm for pm in party_movies if pm.num_votes == max_votes]
        # decide winner state
        winner = None
        if max_votes > 0:
            if len(tied_movies) == 1:
                winner = {
                    'status': 'clear winner',
                    'movie_id': tied_movies[0].movie.id,
                    'movie_title': tied_movies[0].movie.title,
                    'votes': max_votes
                }
            else:
                winner = {
                    'status': 'tie',
                    'votes': max_votes,
                    'tied_movies': [
                        {
                            'movie_id': pm.movie.id,
                            'movie_title': pm.movie.title
                        }
                        for pm in tied_movies
                    ]
                }    
        serializer = PartyMovieSerializer(party_movies, many=True,context={'max_votes': max_votes, 'request': request})
        return Response({'movies': serializer.data, 'winner': winner, 'is_creator': request.user == party.creator})
    
class BreakTieView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        party = get_object_or_404(Party, pk=pk)

        # Only creator can break tie
        if request.user != party.creator:
            return Response(
                {'error': 'Only the party creator can break ties'},
                status=403
            )

        # Make sure movie belongs to this party
        party_movies = PartyMovie.objects.filter(party=party)

        if not party_movies:
            return Response(
                {'error': 'No movies in party'},
                status=400
            )

        # Count votes for each movie
        for party_movie in party_movies:
            party_movie.num_votes = Vote.objects.filter(party=party, movie=party_movie.movie).count()

        # Find max votes 
        max_votes = max(pm.num_votes for pm in party_movies)
        # Find all movies with max votes (tied movies)
        tied_movies = [pm for pm in party_movies if pm.num_votes == max_votes]
        # Validate there is a tie 
        if len(tied_movies) <= 1:
            return Response(
                {'error': 'No tie to break - there is a clear winner'},
                status=400
            )
        # random selection of winner from tie
        winner = random.choice(tied_movies)
        # set winner 
        party.winning_movie = winner.movie
        party.save()
        return Response({
            'message': 'Tie broken successfully',
            'winning_movie': {
                'id': winner.movie.id,
                'title': winner.movie.title,
                'votes': max_votes
            }
        })

    
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
