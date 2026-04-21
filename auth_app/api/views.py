from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from .serializers import RegistrationSerializer, LoginSerializer

class RegistrationView(APIView):
    """
    API view to handle user registration.
    
    Responds to POST requests to create a new user account
    and automatically generates an authentication token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Create a new user.

        Requires fullname, email, password, and repeated_password
        in the request payload.

        Returns:
            Response: A dictionary containing the auth token, fullname,
                email, and user_id on success (HTTP 201), or validation
                errors on failure (HTTP 400).
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
    API view to handle user authentication.
    
    Accepts email and password to authenticate a user and returns
    an authentication token upon success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate a user and generate/retrieve an auth token.
        
        Requires email and password in the request payload.

        Returns:
            Response: Auth token and user details on success (HTTP 200),
                or authentication/validation errors on failure (HTTP 400).
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
        Produce a response depending on whether the user was authenticated.

        Args:
            user (User | None): The user instance returned by authenticate().

        Returns:
            Response: A DRF Response object containing either user data
                and a token (HTTP 200) or an error message (HTTP 400).
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
