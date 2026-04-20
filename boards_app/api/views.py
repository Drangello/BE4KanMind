from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from boards_app.models import Board
from .serializers import BoardSerializer, MemberSerializer
from .permissions import IsBoardOwnerOrReadOnly, IsBoardMember
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

class BoardViewSet(viewsets.ModelViewSet):
    """
    CRUD for Boards.
    """
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardOwnerOrReadOnly]

    def get_queryset(self):
        """
        Filter boards by membership and add aggregation.
        """
        user = self.request.user
        qs = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        return qs.annotate(members_count=Count('members'))

    def perform_create(self, serializer):
        """
        Set the owner to the current user upon creation.
        """
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)

class EmailCheckView(APIView):
    """
    Checks if a given email is registered and returns public user details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({"error": "Email parameter required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if user:
            return Response(MemberSerializer(user).data, status=status.HTTP_200_OK)
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
