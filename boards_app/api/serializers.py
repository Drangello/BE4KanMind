from rest_framework import serializers
from django.contrib.auth import get_user_model
from boards_app.models import Board
from tasks_app.models import Task

User = get_user_model()

class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer to represent a simplified User object for board membership.
    """
    class Meta:
        model = User
        fields = ('id', 'fullname', 'email')

class TaskNestedSerializer(serializers.ModelSerializer):
    """
    Serializer to represent tasks when nested inside a board detail view.
    Includes read-only serialized data for assignees and reviewers.
    """
    assignee = MemberSerializer(read_only=True)
    reviewer = MemberSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count')

    def get_comments_count(self, obj):
        # Placeholder until comments are modeled
        return 0

class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Board instances.
    
    Includes aggregated statistics such as member counts, total tasks, 
    tasks to do, and high priority tasks. Data is populated via viewset annotations.
    """
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id')

class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a single Board instance.
    
    Provides comprehensive board details, including a full list of members
    and all nested tasks.
    """
    owner_id = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'title', 'owner_id', 'members', 'tasks')

class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Board instances.
    
    Accepts a list of primary keys for assigning members.
    """
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'title', 'members')
