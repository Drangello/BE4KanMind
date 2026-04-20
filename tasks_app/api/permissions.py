from rest_framework import permissions

class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """
    Object-level permission to allow only task creators or board owners to delete.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.method in ['PUT', 'PATCH']:
            # Assume update permissibility is caught by valid membership logic
            # meaning anyone in the board can update a task.
            return True
        # For DELETE
        return obj.creator == request.user or obj.board.owner == request.user
