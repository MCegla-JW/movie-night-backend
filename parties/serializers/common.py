from rest_framework.serializers import ModelSerializer
from parties.models import Party

class PartySerializer(ModelSerializer):
    class Meta:
        model = Party
        fields = '__all__'
        read_only_fields = ['join_code', 'creator', 'members']
    