from rest_framework.serializers import ModelSerializer
from parties.models import Party
from movies.models import Movie
from users.models import User 

class MovieSerializer(ModelSerializer):

    class Meta:
        model = Movie
        fields = ['id',
                  'tmdb_id',
                  'title',
                  'poster',
                  'release_date',
                  ]