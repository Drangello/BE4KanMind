from rest_framework import serializers
from django.contrib.auth import get_user_model
from boards_app.models import Board

User = get_user_model()

class MemberSerializer(serializers.ModelSerializer):
    """
    Nested serializer for displaying board members and owners.
    """
    class Meta:
        model = User
        fields = ('id', 'fullname', 'email')

class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board model.
    """
    owner = MemberSerializer(read_only=True)
    members = MemberSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='members',
        many=True,
        write_only=True,
        required=False
    )
    members_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'created_at', 'owner', 'members', 'member_ids', 'members_count')
