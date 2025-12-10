from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers.common import UserSerializer

# Create your views here.
class SignUpView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message:' 'Registration successful', 201})
    
