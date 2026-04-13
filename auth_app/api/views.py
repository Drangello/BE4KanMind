from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from .serializers import RegistrationSerializer, LoginSerializer

class RegistrationView(APIView):
    """
    Handles user registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Create a new user and return an auth token.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'fullname': user.fullname,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Handles user login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate a user and return an auth token.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            return self._handle_authentication(user)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _handle_authentication(self, user):
        """
        Helper to handle the result of authentication.
        """
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'fullname': user.fullname,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        return Response(
            {"error": "Invalid Credentials"},
            status=status.HTTP_400_BAD_REQUEST
        )
