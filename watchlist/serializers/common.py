from rest_framework.serializers import ModelSerializer
from movies.models import Watchlist

class WatchlistSerializer(ModelSerializer):
    class Meta: 
        model = Watchlist
        fields = '__all__'
    