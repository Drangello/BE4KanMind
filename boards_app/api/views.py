from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from boards_app.models import Board
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardCreateUpdateSerializer, MemberSerializer
from .permissions import IsBoardMember, IsBoardOwner
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and manipulating Board instances.

    Provides standard CRUD operations.
    - list: Returns boards where the user is an owner or member.
    - retrieve: Returns detailed board data including nested tasks.
    - create/update: Handles board property changes and member assignment.
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMember()]

    def get_serializer_class(self):
        if self.action == 'list':
            return BoardListSerializer
        elif self.action == 'retrieve':
            return BoardDetailSerializer
        return BoardCreateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        return qs.annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tasks', distinct=True),
            tasks_to_do_count=Count('tasks', filter=Q(tasks__status='to-do'), distinct=True),
            tasks_high_prio_count=Count('tasks', filter=Q(tasks__priority='high'), distinct=True)
        )

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        members = serializer.validated_data.get('members', [])
        board.members.set(members)
        board.members.add(self.request.user)

    def perform_update(self, serializer):
        board = serializer.save()
        if 'members' in serializer.validated_data:
            members = serializer.validated_data['members']
            board.members.set(members)
            board.members.add(board.owner)

class EmailCheckView(APIView):
    """
    API view to check if a user with a given email exists.

    Used primarily to find users to add as board members.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({"error": "Email missing"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if user:
            return Response({
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname
            }, status=status.HTTP_200_OK)
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
