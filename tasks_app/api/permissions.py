from rest_framework import permissions

class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """
    Object-level permission:
    - SAFE_METHODS & PUT/PATCH: must be board member/owner.
    - DELETE: must be creator or owner.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board
        
        is_member = user == board.owner or user in board.members.all()
        
        if request.method in permissions.SAFE_METHODS or request.method in ['PUT', 'PATCH']:
            return is_member
            
        if request.method == 'DELETE':
            return user == obj.creator or user == board.owner
        return False

class IsCommentAuthor(permissions.BasePermission):
    """
    Object-level permission:
    - DELETE: must be author.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
