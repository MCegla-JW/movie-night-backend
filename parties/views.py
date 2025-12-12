from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from .models import Party, PartyMovie
from rest_framework.exceptions import NotFound
from .serializers.common import PartySerializer
from django.db.models import Q
import uuid

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
        created_party = serializer.save(creator = request.user, join_code = uuid.uuid4())
        creator = request.user
        created_party.members.add(creator)
        return Response(serializer.data, 201)


    # class PartyItemsView(APIView):
    #     permission_classes = [IsAuthenticated]

    #     # helper function 
    #     def get_party_item(self, pk):