from rest_framework import permissions

class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """
    Object-level permission for Tasks.
    
    - SAFE_METHODS & PUT/PATCH: The user must be a member or owner of the task's board.
    - DELETE: The user must be the original creator of the task, or the board owner.
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
    Object-level permission for Comments.
    
    - SAFE_METHODS & PUT/PATCH: User must be a member of the task's board.
    - DELETE: Only the author of the comment may delete it, and must be a board member.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.task.board
        is_member = user == board.owner or user in board.members.all()
        
        if request.method in permissions.SAFE_METHODS:
            return is_member
        return obj.author == request.user and is_member
