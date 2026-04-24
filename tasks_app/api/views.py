from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound

from tasks_app.models import Task, Comment
from boards_app.models import Board
from .serializers import TaskSerializer, CommentSerializer
from .permissions import IsTaskCreatorOrBoardOwner, IsCommentAuthor


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskCreatorOrBoardOwner]

    def get_queryset(self):
        return Task.objects.all()

    def get_object(self):
        obj = Task.objects.filter(id=self.kwargs.get('pk')).first()

        if not obj:
            raise NotFound("Task not found.")

        return obj

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.get_queryset().filter(
            Q(board__owner=user) | Q(board__members=user)
        ).distinct()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request, *args, **kwargs):
        board_id = request.data.get('board')
        if board_id:
            if not Board.objects.filter(id=board_id).exists():
                raise NotFound("Board not found.")
        
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        tasks = self.get_queryset().filter(
            Q(board__owner=request.user) | Q(board__members=request.user),
            Q(assignee=request.user) | Q(reviewer=request.user)
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        tasks = self.get_queryset().filter(
            Q(board__owner=request.user) | Q(board__members=request.user),
            reviewer=request.user
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class TaskCommentListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def _get_task(self):
        task = Task.objects.filter(id=self.kwargs.get('task_id')).first()

        if not task:
            raise NotFound("Task not found.")

        return task

    def get_queryset(self):
        task = self._get_task()
        return Comment.objects.filter(task=task).order_by('created_at')

    def perform_create(self, serializer):
        task = self._get_task()
        serializer.save(author=self.request.user, task=task)


class TaskCommentDetailView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_object(self):
        task = Task.objects.filter(id=self.kwargs.get('task_id')).first()

        if not task:
            raise NotFound("Task not found.")

        comment = Comment.objects.filter(
            id=self.kwargs.get('comment_id'),
            task=task
        ).first()

        if not comment:
            raise NotFound("Comment not found.")

        self.check_object_permissions(self.request, comment)
        return comment