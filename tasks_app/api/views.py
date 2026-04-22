from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from tasks_app.models import Task
from .serializers import TaskSerializer
from .permissions import IsTaskCreatorOrBoardOwner

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and manipulating Task instances.
    
    Provides standard CRUD operations, restricted to boards the user has access to.
    Includes custom actions for retrieving tasks specifically assigned to or
    being reviewed by the current user.
    """
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
        tasks = self.get_queryset().filter(
            Q(assignee=request.user) | Q(reviewer=request.user)
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        tasks = self.get_queryset().filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

from .serializers import CommentSerializer
from .permissions import IsCommentAuthor
from tasks_app.models import Comment
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

class TaskCommentListView(generics.ListCreateAPIView):
    """
    GET /api/tasks/{task_id}/comments/
    POST /api/tasks/{task_id}/comments/
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def _get_task(self):
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        user = self.request.user
        if user != task.board.owner and user not in task.board.members.all():
            raise PermissionDenied("You must be a member of the board to access comments.")
        return task

    def get_queryset(self):
        task = self._get_task()
        return Comment.objects.filter(task=task).order_by('created_at')

    def perform_create(self, serializer):
        task = self._get_task()
        serializer.save(author=self.request.user, task=task)

class TaskCommentDetailView(generics.DestroyAPIView):
    """
    DELETE /api/tasks/{task_id}/comments/{comment_id}/
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    
    def get_object(self):
        task_id = self.kwargs.get('task_id')
        comment_id = self.kwargs.get('comment_id')
        task = get_object_or_404(Task, id=task_id)
        
        user = self.request.user
        if user != task.board.owner and user not in task.board.members.all():
            raise PermissionDenied("You must be a member of the board to interact with comments.")
            
        comment = get_object_or_404(Comment, id=comment_id, task=task)
        self.check_object_permissions(self.request, comment)
        return comment
