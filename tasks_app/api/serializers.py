from rest_framework import serializers
from tasks_app.models import Task
from boards_app.models import Board
from django.contrib.auth import get_user_model

User = get_user_model()

class UserNestedSerializer(serializers.ModelSerializer):
    """
    Minimal User serializer for nesting within a Task to show assignee/reviewer.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'fullname')

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task instances.
    
    Handles read/write of task data, enforcing board membership validation
    for assignees, reviewers, and the task creator.
    """
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', allow_null=True, required=False, write_only=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', allow_null=True, required=False, write_only=True
    )
    comments_count = serializers.SerializerMethodField()
    status = serializers.ChoiceField(choices=["to-do", "in-progress", "review", "done"], default="to-do")
    priority = serializers.ChoiceField(choices=["low", "medium", "high"], default="medium")

    class Meta:
        model = Task
        fields = ('id', 'board', 'title', 'description', 'status', 'priority', 
                  'assignee', 'reviewer', 'assignee_id', 'reviewer_id', 'due_date', 'comments_count')

    def get_comments_count(self, obj):
        if hasattr(obj, 'comments'):
            return obj.comments.count()
        return 0

    def validate_board(self, value):
        from rest_framework.exceptions import PermissionDenied
        if self.instance and self.instance.board != value:
            raise serializers.ValidationError("Cannot move a task to a different board.")
        user = self.context['request'].user
        if user != value.owner and user not in value.members.all():
            raise PermissionDenied("You must belong to board to create task.")
        return value

    def validate(self, attrs):
        board = attrs.get('board')
        if not board and self.instance:
            board = self.instance.board
        
        self._validate_board_role(attrs.get('assignee'), board, "assignee")
        self._validate_board_role(attrs.get('reviewer'), board, "reviewer")
        return attrs

    def _validate_board_role(self, user_obj, board, field_name):
        if user_obj and user_obj not in board.members.all() and user_obj != board.owner:
            raise serializers.ValidationError({field_name: "User is not a board member."})

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment instances.
    
    Author is automatically populated via view's perform_create method.
    """
    author = serializers.CharField(source='author.fullname', read_only=True)

    class Meta:
        from tasks_app.models import Comment
        model = Comment
        fields = ('id', 'author', 'content', 'created_at')
        read_only_fields = ('author',)
