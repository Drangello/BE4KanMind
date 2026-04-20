from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from tasks_app.models import Task
from .serializers import TaskSerializer
from .permissions import IsTaskCreatorOrBoardOwner

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskCreatorOrBoardOwner]

    def get_queryset(self):
        user = self.request.user
        # Filters tasks down to only those within boards the user has access to
        return Task.objects.filter(
            Q(board__owner=user) | Q(board__members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        tasks = self.get_queryset().filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        tasks = self.get_queryset().filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
