from rest_framework import serializers
from tasks_app.models import Task
from boards_app.models import Board
from django.contrib.auth import get_user_model

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'priority', 'due_date', 'board', 'assignee', 'reviewer', 'creator')
        read_only_fields = ('creator',)

    def validate_board(self, value):
        if self.instance and self.instance.board != value:
            raise serializers.ValidationError("Cannot move a task to a different board.")
        return value

    def validate(self, attrs):
        board = attrs.get('board')
        if not board and self.instance:
            board = self.instance.board
            
        assignee = attrs.get('assignee')
        if assignee and assignee not in board.members.all() and assignee != board.owner:
            raise serializers.ValidationError({"assignee": "User is not a board member."})
            
        reviewer = attrs.get('reviewer')
        if reviewer and reviewer not in board.members.all() and reviewer != board.owner:
            raise serializers.ValidationError({"reviewer": "User is not a board member."})
            
        return attrs
