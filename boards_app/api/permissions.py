from rest_framework import permissions

class IsBoardOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of a board to edit or delete it.
    Members can read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user == obj.owner or request.user in obj.members.all()
        return obj.owner == request.user

class IsBoardMember(permissions.BasePermission):
    """
    Permission to only allow members or owners to interact with the board.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()
