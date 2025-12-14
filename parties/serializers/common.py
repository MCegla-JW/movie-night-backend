from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from parties.models import Party, PartyMovie, Vote
from movies.models import Movie
from users.models import User
from users.serializers.common import UserSerializer
from movies.serializers.common import MovieSerializer
from rest_framework import serializers
from django.db.models import Q, Count, Max


class PartySerializer(ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)
    class Meta:
        model = Party
        fields = '__all__'
        read_only_fields = ['join_code', 'creator', 'members']
    
class PartyMovieSerializer(ModelSerializer):
        party = PrimaryKeyRelatedField(queryset=Party.objects.all())
        movie = MovieSerializer()
        added_by_user = PrimaryKeyRelatedField(queryset=User.objects.all())
        is_winner = serializers.SerializerMethodField(read_only=True)
        num_votes = serializers.IntegerField(read_only=True)

        class Meta:
             model = PartyMovie
             fields = ['party', 'movie', 'added_by_user', 'is_winner', 'num_votes']
        
        def get_is_winner(self, obj):
            # Votes per movie
            max_votes = self.context.get('max_votes', 0)
            return getattr(obj, 'num_votes', 0) == max_votes

