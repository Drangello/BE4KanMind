"""
Views for handling Task-related API endpoints.
Provides endpoints for creating, reading, updating, and deleting Tasks,
as well as managing Task Comments.
"""
from django.db.models import Q
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tasks_app.models import Comment, Task
from .permissions import IsCommentAuthor, IsTaskCreatorOrBoardOwner
from .serializers import CommentSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and manipulating Task instances.
    Provides standard CRUD operations along with custom query sets 
    based on the user's board membership.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskCreatorOrBoardOwner]

    def get_queryset(self):
        """
        Base queryset containing all tasks. 
        Object-level permissions filter this down for individual lookups.
        """
        return Task.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Filters the task list so a user only sees tasks from boards
        where they are either the owner or a member.
        """
        user = request.user
        queryset = self.get_queryset().filter(
            Q(board__owner=user) | Q(board__members=user)
        ).distinct()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Automatically assigns the logged-in user as the creator of the task.
        """
        serializer.save(creator=self.request.user)


    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        """
        Custom endpoint returning tasks explicitly assigned to or reviewed by the user.
        """
        tasks = self.get_queryset().filter(
            Q(board__owner=request.user) | Q(board__members=request.user),
            Q(assignee=request.user) | Q(reviewer=request.user)
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        """
        Custom endpoint returning tasks where the user is assigned as the reviewer.
        """
        tasks = self.get_queryset().filter(
            Q(board__owner=request.user) | Q(board__members=request.user),
            reviewer=request.user
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class TaskCommentListView(generics.ListCreateAPIView):
    """
    API view to list all comments for a specific task or add a new comment.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def _get_task(self):
        """
        Helper method to retrieve the associated task and ensure the user
        has the appropriate permissions to view its comments.
        """
        task = Task.objects.filter(id=self.kwargs.get('task_id')).first()

        if not task:
            raise NotFound("Task not found.")

        user = self.request.user
        if user != task.board.owner and user not in task.board.members.all():
            raise PermissionDenied("You do not have permission to access this task.")

        return task

    def get_queryset(self):
        """
        Returns all comments belonging to the requested task, ordered by creation time.
        """
        task = self._get_task()
        return Comment.objects.filter(task=task).order_by('created_at')

    def perform_create(self, serializer):
        """
        Saves a new comment, securely setting the author to the current user
        and linking it to the specified task.
        """
        task = self._get_task()
        serializer.save(author=self.request.user, task=task)


class TaskCommentDetailView(generics.DestroyAPIView):
    """
    API view to delete a specific comment on a task.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_object(self):
        """
        Retrieves the comment, ensuring that the task exists and the user
        is a valid member of the corresponding board, followed by object-level checks.
        """
        task = Task.objects.filter(id=self.kwargs.get('task_id')).first()

        if not task:
            raise NotFound("Task not found.")

        user = self.request.user
        if user != task.board.owner and user not in task.board.members.all():
            raise PermissionDenied("You do not have permission to access this task.")

        comment = Comment.objects.filter(
            id=self.kwargs.get('comment_id'),
            task=task
        ).first()

        if not comment:
            raise NotFound("Comment not found.")

        self.check_object_permissions(self.request, comment)
        return comment