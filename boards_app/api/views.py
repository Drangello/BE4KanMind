from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_app.models import Board
from .permissions import IsBoardMember, IsBoardOwner
from .serializers import (
    BoardCreateUpdateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardPatchResponseSerializer,
)

User = get_user_model()


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and manipulating Board instances.
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
        return Board.objects.annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tasks', distinct=True),
            tasks_to_do_count=Count(
                'tasks',
                filter=Q(tasks__status='to-do'),
                distinct=True
            ),
            tasks_high_prio_count=Count(
                'tasks',
                filter=Q(tasks__priority='high'),
                distinct=True
            )
        )


    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.get_queryset().filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        board = self.get_queryset().get(id=serializer.instance.id)
        response_serializer = BoardListSerializer(board)
        headers = self.get_success_headers(serializer.data)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        response_serializer = BoardPatchResponseSerializer(instance)
        return Response(response_serializer.data)


class EmailCheckView(APIView):
    """
    Check if a user with a given email exists.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')

        if not email:
            return Response(
                {"error": "Email missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()

        if user:
            return Response({
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname
            }, status=status.HTTP_200_OK)

        return Response(
            {"error": "Not found"},
            status=status.HTTP_404_NOT_FOUND
        )