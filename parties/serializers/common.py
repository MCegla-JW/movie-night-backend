from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from parties.models import Party, PartyMovie
from movies.models import Movie
from users.models import User
from users.serializers.common import UserSerializer


class PartySerializer(ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)
    class Meta:
        model = Party
        fields = '__all__'
        read_only_fields = ['join_code', 'creator', 'members']
    


class PartyMovieSerializer(ModelSerializer):
        party = PrimaryKeyRelatedField(queryset=Party.objects.all())
        movie = PrimaryKeyRelatedField(queryset=Movie.objects.all())
        added_by_user = PrimaryKeyRelatedField(queryset=User.objects.all())

        class Meta:
             model = PartyMovie
             fields = '__all__'


