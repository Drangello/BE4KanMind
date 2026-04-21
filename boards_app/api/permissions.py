from rest_framework import permissions

class IsBoardOwner(permissions.BasePermission):
    """
    Object-level permission to allow only the owner of a board to modify or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsBoardMember(permissions.BasePermission):
    """
    Object-level permission to allow only board owners and members to access a board.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()
