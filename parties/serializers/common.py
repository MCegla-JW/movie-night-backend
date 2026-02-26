from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from parties.models import Party, PartyMovie, Vote
from users.models import User
from users.serializers.common import UserSerializer
from movies.serializers.common import MovieSerializer
from rest_framework import serializers


class PartyMovieSerializer(ModelSerializer):
    party = PrimaryKeyRelatedField(queryset=Party.objects.all())
    movie = MovieSerializer()
    added_by_user = PrimaryKeyRelatedField(queryset=User.objects.all())
    is_winner = serializers.SerializerMethodField(read_only=True)
    num_votes = serializers.IntegerField(read_only=True)
    user_has_voted = serializers.SerializerMethodField()

    class Meta:
        model = PartyMovie
        fields = ['party', 'movie', 'added_by_user', 'is_winner', 'num_votes', 'user_has_voted']

    def get_is_winner(self, obj):
        max_votes = self.context.get('max_votes', 0)
        if max_votes == 0:
            return False
        return obj.num_votes == max_votes
    
    def get_user_has_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Vote.objects.filter(
                user=request.user,
                party=obj.party,
                movie=obj.movie
            ).exists()
        return False


class PartySerializer(ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)
    movies = PartyMovieSerializer(source='party_movies', many=True, read_only=True)

    class Meta:
        model = Party
        fields = '__all__'
        read_only_fields = ['join_code', 'creator', 'members']


